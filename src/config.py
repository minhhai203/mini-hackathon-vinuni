"""Application settings."""
import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover - keeps static analysis usable before deps install.
    BaseSettings = object
    SettingsConfigDict = dict


class Settings(BaseSettings):
    app_name: str = "Mini Hackathon VinUni"
    app_version: str = "0.1.0"
    environment: str = "development"

    if BaseSettings is not object:
        model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")


settings = Settings()


class LLMSettings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_base_url: str = ""
    openai_max_output_tokens: int = 450
    llm_enabled: bool = True

    if BaseSettings is not object:
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")


llm_settings = LLMSettings()
# Load .env manually so non-prefixed keys (GOOGLE_API_KEY, GEMINI_MODEL) are available
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                if _k.strip() not in os.environ:
                    os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

# Provider selection
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "google")

# Google / Gemini
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

# OpenAI
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Local (Ollama / LM Studio / vLLM)
LOCAL_LLM_BASE_URL: str = os.getenv("LOCAL_LLM_BASE_URL", "")
LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "")
LOCAL_LLM_API_KEY: str = os.getenv("LOCAL_LLM_API_KEY", "no-key")
