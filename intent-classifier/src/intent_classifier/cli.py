from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .config import load_config
from .llm_client import LLMClient
from .orchestrator import IntentChatEngine
from .persona import load_persona


def main() -> None:
    console = Console()
    config = load_config()

    persona_path = config.persona_path
    if not persona_path.is_absolute():
        persona_path = Path.cwd() / persona_path
    persona = load_persona(persona_path)

    engine = IntentChatEngine(llm=LLMClient(config), persona=persona)

    console.print(
        Panel.fit(
            f"Intent Chat CLI\n"
            f"analysis_model={config.analysis_model}\n"
            f"response_model={config.response_model}\n"
            f"persona={persona.display_name}",
            title="Two-Stage LLM",
        )
    )
    console.print("输入 `exit` 退出。\n")

    while True:
        user_text = console.input("[bold cyan]You > [/]").strip()
        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            break

        analysis = engine.analyze_turn(user_text=user_text)
        analysis_json = json.dumps(
            analysis.model_dump(),
            ensure_ascii=False,
            indent=2,
        )
        console.print("\n[bold yellow]Analysis JSON:[/]")
        console.print(Syntax(analysis_json, "json", line_numbers=False))

        console.print("[bold green]Assistant > [/]", end="")
        turn = engine.respond_turn(
            user_text=user_text,
            analysis=analysis,
            on_response_delta=lambda d: console.print(d, end=""),
        )
        console.print()
        # Reprint final response after streamed output for clarity.
        # console.print(f"[dim]Final:[/] {turn.streamed_response}")
        # console.print()


if __name__ == "__main__":
    main()
