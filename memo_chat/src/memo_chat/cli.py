"""Entry point: wire settings → LLMClient → MemoryService → TUI."""

from __future__ import annotations

from memo_chat.llm import LLMClient, setup_logging
from memo_chat.repository import MemoryRepository
from memo_chat.service import MemoryService
from memo_chat.settings import get_settings
from memo_chat.tui import MemoChatApp


def main() -> None:
    s = get_settings()
    setup_logging(s.log_file)

    repo = MemoryRepository(s.database_url)
    repo.init_schema()

    llm = LLMClient(
        api_key=s.openai_api_key,
        base_url=s.openai_base_url,
        chat_model=s.chat_model,
        embed_model=s.embedding_model,
        embed_dims=s.embedding_dims,
    )
    svc = MemoryService(repo, llm)

    app = MemoChatApp(
        svc,
        llm.stream,
        agent_id=s.agent_id,
        session_id=s.session_id,
        history_turns=s.history_turns,
    )
    app.run()


if __name__ == "__main__":
    main()
