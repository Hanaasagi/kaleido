from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConfidenceScores(BaseModel):
    overall: float = Field(ge=0.0, le=1.0)
    intent: float = Field(ge=0.0, le=1.0)
    emotion: float = Field(ge=0.0, le=1.0)
    interaction_need: float = Field(ge=0.0, le=1.0)


class EmotionState(BaseModel):
    primary: str
    valence: Literal["negative", "neutral", "positive", "mixed"]
    arousal: Literal["low", "medium", "high"]
    intensity: float = Field(ge=0.0, le=1.0)


class AmbiguityAssessment(BaseModel):
    is_ambiguous: bool
    reasons: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)


class ResponseStrategy(BaseModel):
    style: Literal[
        "empathic_reflection",
        "curious_followup",
        "light_banter",
        "gentle_support",
        "practical_advice",
        "celebratory_alignment",
        "clarifying_question",
        "boundary_refusal",
    ]
    empathy_level: Literal["low", "medium", "high"]
    directness: Literal["soft", "balanced", "direct"]
    ask_followup: bool
    followup_goal: str = ""
    avoid: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)


class IntentAnalysis(BaseModel):
    language: str
    primary_intent: str
    secondary_intent: str = "none"
    speech_act: str
    interaction_need: str
    user_goal: str
    topic: str
    key_entities: list[str] = Field(default_factory=list)
    time_scope: Literal["past", "present", "future", "unknown"]
    emotional_state: EmotionState
    social_signal: str
    risk_flags: list[str] = Field(default_factory=list)
    ambiguity: AmbiguityAssessment
    confidence: ConfidenceScores
    strategy: ResponseStrategy
    candidate_followups: list[str] = Field(default_factory=list)
    response_blueprint: str


class TurnResult(BaseModel):
    analysis: IntentAnalysis
    streamed_response: str
