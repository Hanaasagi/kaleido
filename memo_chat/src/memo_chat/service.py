from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from memo_chat.llm import LLMClient
from memo_chat.models import Memory, MemoryFilter
from memo_chat.prompts import fmt_query_expand, fmt_summarize_turn
from memo_chat.repository import MemoryRepository
from memo_chat.rrf import (
    apply_type_weights,
    collect_mems,
    paginate,
    rrf_merge,
    sort_by_score,
)

DEFAULT_MIN_SCORE = 0.3


def relative_age(t: datetime | None) -> str:
    if t is None:
        return "just now"
    now = datetime.now(timezone.utc)
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    sec = (now - t).total_seconds()
    if sec < 60:
        return "just now"
    for unit_sec, name in [
        (365 * 86400, "year"),
        (30 * 86400, "month"),
        (7 * 86400, "week"),
        (86400, "day"),
        (3600, "hour"),
        (60, "minute"),
    ]:
        if sec >= unit_sec:
            v = int(sec // unit_sec)
            return f"{v} {name}{'s' if v != 1 else ''} ago"
    return "just now"


def populate_relative_age(memories: list[Memory]) -> list[Memory]:
    for m in memories:
        m.relative_age = relative_age(m.updated_at or m.created_at)
    return memories


def set_scores(page: list[Memory], scores: dict[str, float]) -> list[Memory]:
    for m in page:
        if m.score is None:
            m.score = scores.get(m.id, 0.0)
    return page


@dataclass
class ExpandResult:
    rewritten: str
    keywords: list[str]


class MemoryService:
    def __init__(self, repo: MemoryRepository, llm: LLMClient) -> None:
        self._repo = repo
        self._llm = llm

    def search(self, flt: MemoryFilter) -> tuple[list[Memory], int]:
        """Single-query hybrid search (vector + keyword) with RRF fusion."""
        if not flt.query.strip():
            return [], 0
        limit = flt.limit if 0 < flt.limit <= 200 else 10
        offset = max(flt.offset, 0)
        fetch_limit = limit * 3

        qv = self._llm.embed(flt.query)
        vec_results = self._repo.vector_search(qv, flt, fetch_limit)
        min_score = flt.min_score or DEFAULT_MIN_SCORE
        vec_results = [m for m in vec_results if (m.score or 0) >= min_score]
        kw_results = self._repo.keyword_search(flt.query, flt, fetch_limit)

        scores = rrf_merge(kw_results, vec_results)
        mems = collect_mems(kw_results, vec_results)
        apply_type_weights(mems, scores)
        merged = sort_by_score(mems, scores)
        page, total = paginate(merged, offset, limit)
        page = set_scores(page, scores)
        return populate_relative_age(page), total

    def query_expand(self, user_text: str) -> ExpandResult:
        """Use LLM to extract keywords and rewrite query for RAG retrieval."""
        try:
            result = self._llm.complete_json(fmt_query_expand(user_text))
            return ExpandResult(
                rewritten=result.get("rewritten") or user_text,
                keywords=[str(k) for k in result.get("keywords") or []],
            )
        except Exception:  # noqa: BLE001
            return ExpandResult(rewritten=user_text, keywords=[])

    def search_with_expand(
        self, user_text: str, *, agent_id: str, limit: int = 8
    ) -> tuple[list[Memory], ExpandResult]:
        """Dual-path RAG: run search on expanded query + each keyword, fuse results.

        Post-processing steps:
        1. Collect results from expanded query (vector+kw) and each keyword (kw only).
        2. Merge all result sets via RRF for deduplication and re-ranking.
        3. Apply type weights and paginate.
        """
        expand = self.query_expand(user_text)
        base_flt = MemoryFilter(agent_id=agent_id, limit=limit)
        fetch_limit = limit * 3

        # Path A: full hybrid search on rewritten query
        flt_a = MemoryFilter(query=expand.rewritten, agent_id=agent_id, limit=limit)
        vec_a = self._llm.embed(expand.rewritten)
        vec_results = self._repo.vector_search(vec_a, flt_a, fetch_limit)
        min_score = DEFAULT_MIN_SCORE
        vec_results = [m for m in vec_results if (m.score or 0) >= min_score]
        kw_results_a = self._repo.keyword_search(expand.rewritten, flt_a, fetch_limit)

        # Path B: keyword-only searches (no embedding cost per keyword)
        kw_results_b: list[Memory] = []
        for kw in expand.keywords:
            if kw.strip():
                flt_kw = MemoryFilter(query=kw, agent_id=agent_id, limit=limit)
                kw_results_b.extend(self._repo.keyword_search(kw, flt_kw, fetch_limit))

        # Fuse all paths via RRF
        all_kw = kw_results_a + kw_results_b
        scores = rrf_merge(all_kw, vec_results)
        mems = collect_mems(all_kw, vec_results)
        apply_type_weights(mems, scores)
        merged = sort_by_score(mems, scores)
        page, _ = paginate(merged, 0, limit)
        page = set_scores(page, scores)
        return populate_relative_age(page), expand

    def create_insight(
        self,
        content: str,
        *,
        agent_id: str = "",
        session_id: str = "",
        tags: list[str] | None = None,
        memory_type: str = "insight",
    ) -> Memory:
        emb = self._llm.embed(content)
        return self._repo.create(
            content=content,
            embedding=emb,
            memory_type=memory_type,
            agent_id=agent_id,
            session_id=session_id,
            tags=tags,
        )

    def ingest_turn(
        self,
        user_text: str,
        assistant_text: str,
        *,
        agent_id: str,
        session_id: str,
    ) -> None:
        """Summarize the turn via LLM, then store as a memory insight."""
        try:
            summary = self._llm.complete(fmt_summarize_turn(user_text, assistant_text))
        except Exception:  # noqa: BLE001
            summary = f"{user_text}\n{assistant_text}"

        summary = summary.strip()
        if not summary or summary == "SKIP":
            return

        self.create_insight(
            summary,
            agent_id=agent_id,
            session_id=session_id,
            tags=["turn"],
        )
