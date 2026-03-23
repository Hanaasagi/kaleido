from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5433/memo_chat"
    openai_base_url: str = "https://openrouter.ai/api/v1"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    embedding_dims: int = 1536
    chat_model: str = "qwen/qwen3.5-flash-02-23"
    agent_id: str = "cli-local"
    session_id: str = "cli-session"
    history_turns: int = 3
    log_file: str = "memo_chat.log"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
