"""LLM client wrapping the openai SDK.

Supports any OpenAI-compatible provider (OpenAI, OpenRouter, etc.) via base_url.
All requests/responses are logged to a configurable file.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator

from json_repair import repair_json
from openai import OpenAI

logger = logging.getLogger("memo_chat.llm")


def setup_logging(log_file: str) -> None:
    """Configure file logging for LLM calls. Call once at startup."""
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logging.getLogger("memo_chat").addHandler(handler)
    logging.getLogger("memo_chat").setLevel(logging.DEBUG)


class LLMClient:
    """Unified client for chat completions and embeddings."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        chat_model: str,
        embed_model: str,
        embed_dims: int,
    ) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.embed_dims = embed_dims

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    def embed(self, text: str) -> list[float]:
        t0 = time.monotonic()
        logger.debug("embed model=%s text_len=%d", self.embed_model, len(text))
        resp = self._client.embeddings.create(
            model=self.embed_model,
            input=text,
            encoding_format="float",
        )
        vec = resp.data[0].embedding
        if len(vec) != self.embed_dims:
            raise ValueError(
                f"embedding dim {len(vec)} != configured {self.embed_dims}"
            )
        logger.debug(
            "embed done dims=%d elapsed=%.3fs", len(vec), time.monotonic() - t0
        )
        return list(vec)

    # ------------------------------------------------------------------
    # Blocking completion (for query expansion, summarization)
    # ------------------------------------------------------------------

    def complete(
        self, messages: list[dict[str, str]], *, temperature: float = 0.2
    ) -> str:
        t0 = time.monotonic()
        logger.debug(
            "complete model=%s temperature=%s messages=%s",
            self.chat_model,
            temperature,
            json.dumps(messages, ensure_ascii=False),
        )
        resp = self._client.chat.completions.create(
            model=self.chat_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
        )
        content = resp.choices[0].message.content or ""
        logger.debug(
            "complete done elapsed=%.3fs response=%s",
            time.monotonic() - t0,
            content[:500],
        )
        return content

    # ------------------------------------------------------------------
    # Streaming completion (for interactive chat)
    # ------------------------------------------------------------------

    def stream(
        self, messages: list[dict[str, str]], *, temperature: float = 0.7
    ) -> Iterator[str]:
        t0 = time.monotonic()
        logger.debug(
            "stream model=%s temperature=%s messages=%s",
            self.chat_model,
            temperature,
            json.dumps(messages, ensure_ascii=False),
        )
        total = ""
        with self._client.chat.completions.stream(
            model=self.chat_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
        ) as s:
            for event in s:
                if event.type == "content.delta":
                    total += event.delta
                    yield event.delta
        logger.debug(
            "stream done elapsed=%.3fs total_len=%d",
            time.monotonic() - t0,
            len(total),
        )

    # ------------------------------------------------------------------
    # JSON completion with repair fallback
    # ------------------------------------------------------------------

    def complete_json(self, messages: list[dict[str, str]]) -> dict:
        raw = self.complete(messages, temperature=0.0)
        raw = raw.strip()
        # Strip markdown fences if model wraps output
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                "complete_json: invalid JSON, attempting repair. raw=%s", raw[:300]
            )
            repaired = repair_json(raw, return_objects=True)
            if isinstance(repaired, dict):
                return repaired
            raise ValueError(f"Could not parse JSON even after repair: {raw[:200]}")
