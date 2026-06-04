"""LLM service boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from src.config import llm_settings


@dataclass
class LLMResult:
    text: str
    used_provider: bool
    provider: str | None = None
    error: str | None = None


class LLMService:
    """OpenAI-backed response writer with safe fallback behavior."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        enabled: bool | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else llm_settings.openai_api_key
        self.model = model or llm_settings.openai_model
        self.base_url = base_url if base_url is not None else llm_settings.openai_base_url
        self.enabled = llm_settings.llm_enabled if enabled is None else enabled
        self.max_output_tokens = max_output_tokens or llm_settings.openai_max_output_tokens

    @property
    def is_configured(self) -> bool:
        return bool(self.enabled and self.api_key and self.model)

    def generate_chatbot_copy(
        self,
        *,
        mode: str,
        user_message: str,
        profile: dict[str, Any],
        cards: list[dict[str, Any]] | None = None,
        followup_questions: list[str] | None = None,
        travel_context: dict[str, Any] | None = None,
        safety_notice: str | None = None,
    ) -> LLMResult:
        """Generate only the human-facing intro/copy, never the card data."""
        if not self.is_configured:
            return LLMResult(text="", used_provider=False, error="LLM is not configured.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            return LLMResult(text="", used_provider=False, error=f"OpenAI SDK is not installed: {exc}")

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        client = OpenAI(**client_kwargs)
        payload = {
            "mode": mode,
            "user_message": user_message,
            "profile": profile,
            "cards": cards or [],
            "followup_questions": followup_questions or [],
            "travel_context": travel_context or {},
            "safety_notice": safety_notice,
        }
        instructions = (
            "You are a warm Vietnamese Vinpearl trip-planning companion inside a travel planner UI. "
            "Write concise Vietnamese user-facing copy only, in a natural 'mình/bạn' tone. "
            "Use the user's own words to reflect their travel vibe before asking anything else. "
            "Do not sound like a form, FAQ, or knowledge-base script. "
            "Do not invent realtime price, room availability, voucher eligibility, cancellation, refund, or booking confirmation. "
            "Do not add new resort options beyond the provided cards. "
            "If mode is risk, warn safely and ask the user to verify with Vinpearl/MyVinpearl or CSKH. "
            "If mode is followup, write one short empathy sentence, then ask at most 2 natural questions selected from the provided follow-up questions. "
            "If destination is missing, offer 2-3 tailored Vinpearl directions based on the user's vibe instead of listing every destination mechanically. "
            "Do not repeat the same question. Do not use numbered lists unless the user explicitly asks for a checklist. "
            "Return plain text only, no Markdown and no HTML tags."
        )

        try:
            response = client.responses.create(
                model=self.model,
                instructions=instructions,
                input=json.dumps(payload, ensure_ascii=False),
                max_output_tokens=self.max_output_tokens,
            )
            text = (response.output_text or "").strip()
            return LLMResult(text=text, used_provider=bool(text), provider="openai")
        except Exception as exc:  # pragma: no cover - network/provider failure.
            return LLMResult(text="", used_provider=False, provider="openai", error=str(exc))
"""Backward-compatibility shim — actual provider logic lives in src/providers/."""

from src.providers import get_provider
from src.providers.base import LLMProvider

try:
    from src.providers.google import GoogleProvider as GeminiService  # legacy alias
except ImportError as exc:  # pragma: no cover - only hit when optional SDK is missing.
    _gemini_import_error = exc

    class GeminiService:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("google-genai is not installed. Run `python -m pip install -r requirements.txt`.") from _gemini_import_error

__all__ = ["get_provider", "GeminiService", "LLMProvider"]
