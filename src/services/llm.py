"""Backward-compatibility shim — actual provider logic lives in src/providers/."""

from src.providers import get_provider
from src.providers.base import LLMProvider
from src.providers.google import GoogleProvider as GeminiService  # legacy alias

__all__ = ["get_provider", "GeminiService", "LLMProvider"]
