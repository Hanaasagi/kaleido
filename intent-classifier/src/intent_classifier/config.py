from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    base_url: str
    analysis_model: str
    response_model: str
    persona_path: Path
    analysis_temperature: float
    response_temperature: float


def load_config() -> AppConfig:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required.")

    return AppConfig(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1").strip(),
        analysis_model=os.getenv("ANALYSIS_MODEL", "openai/gpt-4.1-mini").strip(),
        response_model=os.getenv("RESPONSE_MODEL", "openai/gpt-4.1-mini").strip(),
        persona_path=Path(os.getenv("PERSONA_PATH", "config/personas/girlfriend.toml")),
        analysis_temperature=float(os.getenv("ANALYSIS_TEMPERATURE", "0.1")),
        response_temperature=float(os.getenv("RESPONSE_TEMPERATURE", "0.8")),
    )
