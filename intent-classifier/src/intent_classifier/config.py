from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI API settings
    api_key: str = Field(alias="OPENAI_API_KEY")
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENAI_BASE_URL",
    )

    # Model settings
    analysis_model: str = Field(
        default="openai/gpt-4.1-mini",
        alias="ANALYSIS_MODEL",
    )
    response_model: str = Field(
        default="openai/gpt-4.1-mini",
        alias="RESPONSE_MODEL",
    )

    # Persona settings
    persona_path: Path = Field(
        default=Path("config/personas/girlfriend.toml"),
        alias="PERSONA_PATH",
    )

    # Temperature settings
    analysis_temperature: float = Field(
        default=0.1,
        alias="ANALYSIS_TEMPERATURE",
        ge=0.0,
        le=2.0,
    )
    response_temperature: float = Field(
        default=0.8,
        alias="RESPONSE_TEMPERATURE",
        ge=0.0,
        le=2.0,
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("OPENAI_API_KEY is required.")
        return v

    @field_validator("persona_path", mode="before")
    @classmethod
    def validate_persona_path(cls, v: str | Path) -> Path:
        return Path(v) if isinstance(v, str) else v


def load_config() -> AppConfig:
    """Load and validate application configuration."""
    return AppConfig()
