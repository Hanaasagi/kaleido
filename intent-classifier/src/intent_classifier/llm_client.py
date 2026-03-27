from __future__ import annotations

import json
from typing import Callable

from openai import OpenAI

from .config import AppConfig


class LLMClient:
    def __init__(self, config: AppConfig):
        self._config = config
        self._client = OpenAI(base_url=config.base_url, api_key=config.api_key)

    def analyze_json(self, system_prompt: str, user_prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model=self._config.analysis_model,
            temperature=self._config.analysis_temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Empty analysis response from LLM.")
        return content

    def repair_json(self, user_prompt: str) -> str:
        completion = self._client.chat.completions.create(
            model=self._config.analysis_model,
            temperature=0.0,
            messages=[
                {
                    "role": "system",
                    "content": "You repair JSON to match schema constraints. Output JSON only.",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("Empty repair response from LLM.")
        return content

    def stream_response(
        self,
        system_prompt: str,
        user_prompt: str,
        on_delta: Callable[[str], None],
    ) -> str:
        stream = self._client.chat.completions.create(
            model=self._config.response_model,
            temperature=self._config.response_temperature,
            stream=True,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        full_text: list[str] = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full_text.append(delta)
                on_delta(delta)

        return "".join(full_text).strip()


def to_pretty_json(raw_json: str) -> str:
    parsed = json.loads(raw_json)
    return json.dumps(parsed, ensure_ascii=False, indent=2)
