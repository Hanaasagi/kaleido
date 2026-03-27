from __future__ import annotations

import json
from typing import Callable

from pydantic import ValidationError

from .llm_client import LLMClient
from .models import IntentAnalysis, TurnResult
from .persona import PersonaConfig
from .policy import derive_autonomy_directive
from .prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    build_analysis_repair_user_prompt,
    build_analysis_user_prompt,
    build_response_system_prompt,
    build_response_user_prompt,
)


class IntentChatEngine:
    def __init__(self, llm: LLMClient, persona: PersonaConfig):
        self._llm = llm
        self._persona = persona
        self._history: list[dict[str, str]] = []

    @property
    def history(self) -> list[dict[str, str]]:
        return list(self._history)

    def analyze_turn(self, user_text: str) -> IntentAnalysis:
        analysis_prompt = build_analysis_user_prompt(user_text=user_text, history=self._history)
        raw_analysis = self._llm.analyze_json(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=analysis_prompt,
        )
        return self._parse_analysis_with_repair(raw_analysis)

    def respond_turn(
        self,
        user_text: str,
        analysis: IntentAnalysis,
        on_response_delta: Callable[[str], None],
    ) -> TurnResult:
        autonomy = derive_autonomy_directive(
            user_text=user_text,
            analysis=analysis,
            history=self._history,
            persona=self._persona,
        )
        analysis_for_generation = analysis.model_dump()
        analysis_for_generation.pop("candidate_followups", None)
        analysis_json = json.dumps(analysis_for_generation, ensure_ascii=False, indent=2)
        response_system = build_response_system_prompt(persona_block=self._persona_block())
        response_user = build_response_user_prompt(
            user_text=user_text,
            analysis_json=analysis_json,
            autonomy_directive=autonomy.instruction,
            history=self._history,
        )
        reply = self._llm.stream_response(
            system_prompt=response_system,
            user_prompt=response_user,
            on_delta=on_response_delta,
        )
        self._history.append({"role": "user", "text": user_text})
        self._history.append({"role": "assistant", "text": reply})
        return TurnResult(analysis=analysis, streamed_response=reply)

    def run_turn(self, user_text: str, on_response_delta: Callable[[str], None]) -> TurnResult:
        analysis = self.analyze_turn(user_text)
        return self.respond_turn(user_text=user_text, analysis=analysis, on_response_delta=on_response_delta)

    def _persona_block(self) -> str:
        tone = ", ".join(self._persona.tone)
        style_rules = "\n".join(f"- {rule}" for rule in self._persona.style_rules)
        boundaries = "\n".join(f"- {rule}" for rule in self._persona.boundaries)
        preferences = "\n".join(f"- {rule}" for rule in self._persona.personal_preferences)
        return (
            f"name: {self._persona.display_name}\n"
            f"relationship: {self._persona.relationship}\n"
            f"voice: {self._persona.voice}\n"
            f"default_reply_length: {self._persona.default_reply_length}\n"
            f"assertiveness: {self._persona.assertiveness}\n"
            f"tone: {tone}\n"
            f"style_rules:\n{style_rules}\n"
            f"boundaries:\n{boundaries}\n"
            f"personal_preferences:\n{preferences}\n"
        )

    def _parse_analysis_with_repair(self, raw_json: str) -> IntentAnalysis:
        try:
            normalized = self._normalize_analysis_dict(json.loads(raw_json))
            return IntentAnalysis.model_validate(normalized)
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
            repair_prompt = build_analysis_repair_user_prompt(raw_json=raw_json)
            repaired_raw = self._llm.repair_json(user_prompt=repair_prompt)
            normalized = self._normalize_analysis_dict(json.loads(repaired_raw))
            return IntentAnalysis.model_validate(normalized)

    def _normalize_analysis_dict(self, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError("analysis output is not an object")

        emotional_state = data.get("emotional_state", {})
        if not isinstance(emotional_state, dict):
            emotional_state = {}
            data["emotional_state"] = emotional_state
        emotional_state["valence"] = self._normalize_valence(emotional_state.get("valence"))
        emotional_state["arousal"] = self._normalize_arousal(emotional_state.get("arousal"))
        emotional_state["intensity"] = self._clamp_01(emotional_state.get("intensity", 0.5))

        confidence = data.get("confidence", {})
        if not isinstance(confidence, dict):
            confidence = {}
            data["confidence"] = confidence
        confidence["overall"] = self._clamp_01(confidence.get("overall", 0.5))
        confidence["intent"] = self._clamp_01(confidence.get("intent", confidence["overall"]))
        confidence["emotion"] = self._clamp_01(confidence.get("emotion", confidence["overall"]))
        confidence["interaction_need"] = self._clamp_01(
            confidence.get("interaction_need", confidence["overall"])
        )

        strategy = data.get("strategy", {})
        if not isinstance(strategy, dict):
            strategy = {}
            data["strategy"] = strategy
        strategy["style"] = self._normalize_style(strategy.get("style"))

        return data

    def _normalize_valence(self, value: object) -> str:
        if isinstance(value, (int, float)):
            v = self._clamp_01(value)
            if v < 0.33:
                return "negative"
            if v > 0.67:
                return "positive"
            return "neutral"
        text = str(value or "").strip().lower()
        mapping = {
            "negative": "negative",
            "neg": "negative",
            "neutral": "neutral",
            "positive": "positive",
            "pos": "positive",
            "mixed": "mixed",
        }
        return mapping.get(text, "neutral")

    def _normalize_arousal(self, value: object) -> str:
        if isinstance(value, (int, float)):
            v = self._clamp_01(value)
            if v < 0.33:
                return "low"
            if v > 0.67:
                return "high"
            return "medium"
        text = str(value or "").strip().lower()
        mapping = {
            "low": "low",
            "medium": "medium",
            "med": "medium",
            "mid": "medium",
            "high": "high",
        }
        return mapping.get(text, "medium")

    def _normalize_style(self, value: object) -> str:
        text = str(value or "").strip().lower()
        allowed = {
            "empathic_reflection",
            "curious_followup",
            "light_banter",
            "gentle_support",
            "practical_advice",
            "celebratory_alignment",
            "clarifying_question",
            "boundary_refusal",
        }
        alias = {
            "empathy": "empathic_reflection",
            "reflection": "empathic_reflection",
            "followup": "curious_followup",
            "follow_up": "curious_followup",
            "question": "clarifying_question",
            "suggestion": "practical_advice",
            "advice": "practical_advice",
        }
        mapped = alias.get(text, text)
        if mapped in allowed:
            return mapped
        return "empathic_reflection"

    def _clamp_01(self, value: object) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return 0.5
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v
