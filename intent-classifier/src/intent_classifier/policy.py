from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from .models import IntentAnalysis
from .persona import PersonaConfig


@dataclass(frozen=True)
class AutonomyDirective:
    mode: str
    instruction: str


def derive_autonomy_directive(
    user_text: str,
    analysis: IntentAnalysis,
    history: list[dict[str, str]],
    persona: PersonaConfig,
) -> AutonomyDirective:
    if analysis.risk_flags:
        return AutonomyDirective(
            mode="boundary_refusal",
            instruction=(
                "Set a clear but warm boundary. Do not comply. Briefly explain reason and"
                " offer a safer alternative."
            ),
        )

    if _looks_like_proposal(user_text):
        hour = _extract_hour(user_text)
        if hour is not None and hour >= 22:
            return AutonomyDirective(
                mode="soft_decline",
                instruction=(
                    "Do not directly agree. Politely decline because it is too late, then"
                    " offer an earlier concrete alternative."
                ),
            )

        score = _stable_choice_score(user_text, history)
        assertiveness = max(0.0, min(1.0, getattr(persona, "assertiveness", 0.45)))
        if hour is not None:
            time_counter_threshold = int(65 + 20 * assertiveness)
            if score < time_counter_threshold:
                return AutonomyDirective(
                    mode="soft_counter",
                    instruction=(
                        "Do not directly agree on time. Offer your preferred time window"
                        " naturally, then ask if that works."
                    ),
                )

        counter_threshold = int(30 + 30 * assertiveness)
        decline_threshold = int(45 + 20 * assertiveness)

        if score < counter_threshold:
            return AutonomyDirective(
                mode="soft_counter",
                instruction=(
                    "Do not fully agree. Express your own preference first, then give one"
                    " concrete counter-proposal."
                ),
            )
        if score < decline_threshold:
            return AutonomyDirective(
                mode="soft_decline",
                instruction=(
                    "Do not agree. Gently decline with a natural personal reason, then"
                    " provide one alternative plan."
                ),
            )

    return AutonomyDirective(
        mode="align_or_neutral",
        instruction=(
            "You may align if it feels natural, but avoid people-pleasing tone. Keep your"
            " own mild point of view."
        ),
    )


def _looks_like_proposal(text: str) -> bool:
    markers = [
        "怎么样",
        "要不",
        "可以吗",
        "行吗",
        "好吗",
        "好不好",
        "要不要",
        "how about",
        "shall we",
        "would you like",
    ]
    lowered = text.lower()
    return any(m in lowered for m in markers)


def _extract_hour(text: str) -> int | None:
    matched = re.search(r"(?<!\d)([01]?\d|2[0-3])点", text)
    if not matched:
        return None
    hour = int(matched.group(1))
    if hour <= 12 and re.search(
        r"(今晚|夜里|半夜|深夜|tonight|at night)", text.lower()
    ):
        return min(23, hour + 12)
    return hour


def _stable_choice_score(user_text: str, history: list[dict[str, str]]) -> int:
    seed_material = user_text + "|" + "|".join(turn["text"] for turn in history[-4:])
    digest = hashlib.sha1(seed_material.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100
