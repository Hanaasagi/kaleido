import json
from uuid_extensions import uuid7
from datetime import datetime, timezone
from typing import Any

import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from memo_chat.db import SCHEMA_SQL
from memo_chat.models import Memory, MemoryFilter


def _row_to_memory(row: dict[str, Any]) -> Memory:
    tags = row.get("tags") or []
    if isinstance(tags, str):
        tags = json.loads(tags)
    meta = row.get("metadata")
    if isinstance(meta, str):
        meta = json.loads(meta)
    return Memory(
        id=str(row["id"]),
        content=row["content"],
        memory_type=row.get("memory_type") or "insight",
        source=row.get("source") or "",
        tags=list(tags) if tags else [],
        metadata=meta if isinstance(meta, dict) else None,
        agent_id=row.get("agent_id") or "",
        session_id=row.get("session_id") or "",
        state=row.get("state") or "active",
        version=int(row.get("version") or 1),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        score=float(row["score"]) if row.get("score") is not None else None,
    )


class MemoryRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _connect_bare(self) -> psycopg.Connection:
        return psycopg.connect(self._dsn, autocommit=True)

    def connect(self) -> psycopg.Connection:
        conn = psycopg.connect(self._dsn, autocommit=True)
        register_vector(conn)
        return conn

    def init_schema(self) -> None:
        with self._connect_bare() as conn:
            for raw in SCHEMA_SQL.split(";"):
                stmt = raw.strip()
                if not stmt or stmt.startswith("--"):
                    continue
                conn.execute(stmt)

    def create(
        self,
        *,
        content: str,
        embedding: list[float] | None,
        memory_type: str = "insight",
        agent_id: str = "",
        session_id: str = "",
        tags: list[str] | None = None,
        source: str = "",
    ) -> Memory:
        mid = str(uuid7())
        now = datetime.now(timezone.utc)
        tags = tags or []
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO memories (
                  id, content, tags, metadata, embedding, memory_type, source,
                  agent_id, session_id, state, version, created_at, updated_at
                ) VALUES (
                  %s::uuid, %s, %s::jsonb, NULL, %s, %s, %s, %s, %s, 'active', 1, %s, %s
                )
                """,
                (
                    mid,
                    content,
                    json.dumps(tags, ensure_ascii=False),
                    embedding,
                    memory_type,
                    source,
                    agent_id or None,
                    session_id or None,
                    now,
                    now,
                ),
            )
        return self.get_by_id(mid)

    def get_by_id(self, mid: str) -> Memory:
        with self.connect() as conn:
            conn.row_factory = dict_row
            row = conn.execute(
                "SELECT * FROM memories WHERE id = %s::uuid",
                (mid,),
            ).fetchone()
        if row is None:
            raise KeyError(mid)
        d = dict(row)
        d["score"] = None
        return _row_to_memory(d)

    def vector_search(
        self, query_vec: list[float], flt: MemoryFilter, fetch_limit: int
    ) -> list[Memory]:
        wh: list[str] = ["state = %(st)s", "embedding IS NOT NULL"]
        params: dict[str, Any] = {
            "st": flt.state or "active",
            "qv": query_vec,
            "lim": fetch_limit,
        }
        if flt.agent_id:
            wh.append("agent_id = %(agent_id)s")
            params["agent_id"] = flt.agent_id
        if flt.session_id:
            wh.append("session_id = %(session_id)s")
            params["session_id"] = flt.session_id
        if flt.memory_type:
            wh.append("memory_type = %(mt)s")
            params["mt"] = flt.memory_type
        where_sql = " AND ".join(wh)
        sql = f"""
            SELECT *, (1 - (embedding <=> %(qv)s::vector)) AS score
            FROM memories
            WHERE {where_sql}
            ORDER BY embedding <=> %(qv)s::vector
            LIMIT %(lim)s
        """
        with self.connect() as conn:
            conn.row_factory = dict_row
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_memory(dict(r)) for r in rows]

    def keyword_search(
        self, query: str, flt: MemoryFilter, fetch_limit: int
    ) -> list[Memory]:
        wh: list[str] = ["state = %(st)s"]
        params: dict[str, Any] = {
            "st": flt.state or "active",
            "q": query,
            "lim": fetch_limit,
        }
        if flt.agent_id:
            wh.append("agent_id = %(agent_id)s")
            params["agent_id"] = flt.agent_id
        if flt.session_id:
            wh.append("session_id = %(session_id)s")
            params["session_id"] = flt.session_id
        if flt.memory_type:
            wh.append("memory_type = %(mt)s")
            params["mt"] = flt.memory_type
        where_sql = " AND ".join(wh)
        sql = f"""
            SELECT *, GREATEST(
              similarity(content, %(q)s),
              CASE WHEN content ILIKE '%%' || %(q)s || '%%' THEN 0.3 ELSE 0 END
            ) AS score
            FROM memories
            WHERE {where_sql}
              AND (content ILIKE '%%' || %(q)s || '%%' OR similarity(content, %(q)s) > 0.02)
            ORDER BY score DESC
            LIMIT %(lim)s
        """
        with self.connect() as conn:
            conn.row_factory = dict_row
            rows = conn.execute(sql, params).fetchall()
        return [_row_to_memory(dict(r)) for r in rows]
