"""Provider factory — reads LLM_PROVIDER from env and returns the right LLMProvider."""

from __future__ import annotations

from src.providers.base import LLMProvider


def get_provider() -> LLMProvider:
    """
    Instantiate and return the configured LLM provider.

    Set LLM_PROVIDER in your .env to switch:

        LLM_PROVIDER=google   → Google Gemini (default)
                                needs: GOOGLE_API_KEY, GEMINI_MODEL

        LLM_PROVIDER=openai   → OpenAI GPT
                                needs: OPENAI_API_KEY, OPENAI_MODEL

        LLM_PROVIDER=local    → Local server (Ollama, LM Studio, vLLM …)
                                needs: LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL
                                optional: LOCAL_LLM_API_KEY (default "no-key")
    """
    import os
    provider = os.getenv("LLM_PROVIDER", "google").lower().strip()

    if provider == "google":
        from src.config import GEMINI_MODEL, GOOGLE_API_KEY
        from src.providers.google import GoogleProvider

        if not GOOGLE_API_KEY:
            raise ValueError("LLM_PROVIDER=google requires GOOGLE_API_KEY in .env")
        return GoogleProvider(api_key=GOOGLE_API_KEY, model=GEMINI_MODEL)

    if provider == "openai":
        from src.config import OPENAI_API_KEY, OPENAI_MODEL
        from src.providers.openai_provider import OpenAICompatibleProvider

        if not OPENAI_API_KEY:
            raise ValueError("LLM_PROVIDER=openai requires OPENAI_API_KEY in .env")
        if not OPENAI_MODEL:
            raise ValueError("LLM_PROVIDER=openai requires OPENAI_MODEL in .env")
        return OpenAICompatibleProvider(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)

    if provider == "local":
        from src.config import LOCAL_LLM_API_KEY, LOCAL_LLM_BASE_URL, LOCAL_LLM_MODEL
        from src.providers.openai_provider import OpenAICompatibleProvider

        if not LOCAL_LLM_BASE_URL:
            raise ValueError("LLM_PROVIDER=local requires LOCAL_LLM_BASE_URL in .env (e.g. http://localhost:11434/v1)")
        if not LOCAL_LLM_MODEL:
            raise ValueError("LLM_PROVIDER=local requires LOCAL_LLM_MODEL in .env (e.g. llama3.1)")
        return OpenAICompatibleProvider(
            api_key=LOCAL_LLM_API_KEY or "no-key",
            model=LOCAL_LLM_MODEL,
            base_url=LOCAL_LLM_BASE_URL,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER='{provider}'. "
        "Valid options: google | openai | local"
    )
