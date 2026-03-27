from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


LiteralReplyLength = Literal["short", "medium", "long"]


class PersonaConfig(BaseModel):
    id: str
    display_name: str
    relationship: str
    voice: str
    tone: list[str] = Field(default_factory=list)
    style_rules: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    personal_preferences: list[str] = Field(default_factory=list)
    assertiveness: float = Field(default=0.45, ge=0.0, le=1.0)
    default_reply_length: LiteralReplyLength = "short"


def load_persona(path: Path) -> PersonaConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    return PersonaConfig.model_validate(raw)
