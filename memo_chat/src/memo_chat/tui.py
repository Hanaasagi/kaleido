"""TUI layer: Textual chat interface.

Responsibilities:
- Render conversation (user messages, recall flow, streaming assistant replies)
- Manage in-memory conversation history (configurable turns)
- Delegate all LLM/memory logic to injected callables and MemoryService
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable, Iterator
from typing import Any

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Collapsible, Footer, Header, Input, Markdown, Static

from memo_chat.models import MemoryFilter  # used by _probe_recall
from memo_chat.prompts import fmt_system
from memo_chat.service import MemoryService

# Callable[[messages], Iterator[str]] — yields text chunks
LLMStream = Callable[[list[dict[str, str]]], Iterator[str]]


class MemoChatApp(App[None]):
    """memo-chat TUI — gruvbox theme, collapsible recall, streaming replies."""

    TITLE = "memo-chat"
    THEME = "gruvbox"

    CSS = """
    Screen { background: $background; }

    #chat-scroll {
        height: 1fr;
        padding: 0 2 1 2;
    }

    .user-msg {
        text-align: right;
        color: $accent;
        margin-top: 1;
        padding: 0 1;
    }

    .recall-collapsible { margin: 0 0 0 2; }

    .recall-item {
        color: $text-muted;
        padding: 0 0 0 1;
    }

    .assistant-label {
        color: $success;
        text-style: bold;
        margin-top: 1;
    }

    .assistant-content { margin: 0 0 1 2; }

    .status-msg {
        color: $text-muted;
        text-style: italic;
        padding-left: 2;
    }

    .cmd-output {
        color: $primary;
        padding-left: 2;
        margin-bottom: 1;
    }

    #user-input {
        height: 3;
        border-top: solid $primary-background;
    }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Quit", priority=True)]

    def __init__(
        self,
        svc: MemoryService,
        llm_stream: LLMStream,
        *,
        agent_id: str,
        session_id: str,
        history_turns: int = 3,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.svc = svc
        self.llm_stream = llm_stream
        self.agent_id = agent_id
        self.session_id = session_id
        self._max_history = history_turns * 2  # pairs of user+assistant
        self._history: list[dict[str, str]] = []

    # ── Layout ───────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(id="chat-scroll")
        yield Input(
            placeholder="Message…  /mem <keyword>  /quit",
            id="user-input",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.theme = self.THEME
        self.query_one("#user-input", Input).focus()

    # ── Input routing ─────────────────────────────────────────────────────

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.clear()
        if text.startswith("/"):
            await self._handle_command(text)
        else:
            self._process_turn(text)

    # ── Commands ──────────────────────────────────────────────────────────

    async def _handle_command(self, text: str) -> None:
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        parts = text.split(maxsplit=1)
        cmd, arg = parts[0].lower(), parts[1] if len(parts) > 1 else ""

        if cmd in ("/quit", "/exit"):
            await self.action_quit()
        elif cmd == "/mem":
            if arg:
                self._probe_recall(arg)
            else:
                await scroll.mount(
                    Static("Usage: /mem <keyword>", classes="cmd-output")
                )
                scroll.scroll_end(animate=False)
        else:
            await scroll.mount(
                Static(
                    f"Unknown command: {cmd}  Available: /mem /quit",
                    classes="cmd-output",
                )
            )
            scroll.scroll_end(animate=False)
        self.query_one("#user-input", Input).focus()

    # ── /mem probe ────────────────────────────────────────────────────────

    @work
    async def _probe_recall(self, keyword: str) -> None:
        scroll = self.query_one("#chat-scroll", ScrollableContainer)
        status = Static(f"⟳ Probing {keyword!r}…", classes="status-msg")
        await scroll.mount(status)
        scroll.scroll_end(animate=False)

        flt = MemoryFilter(query=keyword, agent_id=self.agent_id, limit=8)
        try:
            mems, _ = await asyncio.to_thread(self.svc.search, flt)
        except Exception as e:  # noqa: BLE001
            status.update(f"✗ {e}")
            return
        await status.remove()

        items = [
            Static(
                f"[{i}] {m.relative_age}  score={m.score:.3f}\n{m.content}",
                classes="recall-item",
            )
            for i, m in enumerate(mems, 1)
        ] or [Static("(no memories found)", classes="recall-item")]

        await scroll.mount(
            Collapsible(
                *items,
                title=f"/mem {keyword!r} — {len(mems)} results",
                collapsed=False,
                classes="recall-collapsible",
            )
        )
        scroll.scroll_end(animate=False)
        self.query_one("#user-input", Input).focus()

    # ── Main conversation turn ────────────────────────────────────────────

    @work
    async def _process_turn(self, user_text: str) -> None:
        scroll = self.query_one("#chat-scroll", ScrollableContainer)

        # User bubble
        await scroll.mount(Static(f"You  {user_text}", classes="user-msg"))
        scroll.scroll_end(animate=False)

        # ── Step 1: Query expansion ──────────────────────────────────────
        recall_block = Collapsible(
            title="Recall  ⟳ Expanding query…",
            collapsed=True,
            classes="recall-collapsible",
        )
        await scroll.mount(recall_block)
        scroll.scroll_end(animate=False)

        # ── Step 2: Dual-path RAG (expand + keywords), stream items ─────
        contents = recall_block.query_one(Collapsible.Contents)
        try:
            mems, expand = await asyncio.to_thread(
                self.svc.search_with_expand,
                user_text,
                agent_id=self.agent_id,
            )
        except Exception as e:  # noqa: BLE001
            await contents.mount(Static(f"✗ recall failed: {e}", classes="recall-item"))
            mems, expand = [], None

        kw_label = (
            f"  [{', '.join(expand.keywords)}]" if expand and expand.keywords else ""
        )
        recall_block.title = f"Recall  ⟳ Searching…{kw_label}"

        if mems:
            for i, m in enumerate(mems, 1):
                score = f"{m.score:.3f}" if m.score is not None else "?"
                await contents.mount(
                    Static(
                        f"[{i}] {m.relative_age}  score={score}\n{m.content}",
                        classes="recall-item",
                    )
                )
                scroll.scroll_end(animate=False)
                await asyncio.sleep(0.04)
        else:
            await contents.mount(
                Static("(no relevant memories)", classes="recall-item")
            )

        rewritten = expand.rewritten if expand else user_text
        recall_block.title = f"Recall  {len(mems)} memories  [{rewritten}]"

        # ── Step 3: Build messages with history ──────────────────────────
        messages: list[dict[str, str]] = [
            {"role": "system", "content": fmt_system(mems)},
            *self._history,
            {"role": "user", "content": user_text},
        ]

        # ── Step 4: Stream LLM reply ─────────────────────────────────────
        await scroll.mount(Static("Assistant", classes="assistant-label"))
        reply_widget = Markdown("", classes="assistant-content")
        await scroll.mount(reply_widget)
        scroll.scroll_end(animate=False)

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[str | None] = asyncio.Queue()

        def _producer() -> None:
            try:
                for chunk in self.llm_stream(messages):
                    loop.call_soon_threadsafe(queue.put_nowait, chunk)
            except Exception as e:  # noqa: BLE001
                loop.call_soon_threadsafe(queue.put_nowait, f"\n\n[Error] {e}")
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        threading.Thread(target=_producer, daemon=True).start()

        accumulated = ""
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            accumulated += chunk
            await reply_widget.update(accumulated)
            scroll.scroll_end(animate=False)

        # ── Step 5: Update history buffer ────────────────────────────────
        self._history.append({"role": "user", "content": user_text})
        self._history.append({"role": "assistant", "content": accumulated})
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        # ── Step 6: Async ingest (summarize + store) ─────────────────────
        self._ingest_bg(user_text, accumulated)
        self.query_one("#user-input", Input).focus()

    @work(thread=True)
    def _ingest_bg(self, user_text: str, reply: str) -> None:
        try:
            self.svc.ingest_turn(
                user_text,
                reply,
                agent_id=self.agent_id,
                session_id=self.session_id,
            )
        except Exception:  # noqa: BLE001
            pass
