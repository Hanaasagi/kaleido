from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Memory:
    id: str
    content: str
    memory_type: str = "insight"
    source: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] | None = None
    agent_id: str = ""
    session_id: str = ""
    state: str = "active"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    score: float | None = None
    relative_age: str = ""


@dataclass
class MemoryFilter:
    query: str = ""
    tags: list[str] | None = None
    agent_id: str = ""
    session_id: str = ""
    memory_type: str = ""
    state: str = "active"
    limit: int = 10
    offset: int = 0
    min_score: float = 0.0  # 0 => use default 0.3 for vector branch
