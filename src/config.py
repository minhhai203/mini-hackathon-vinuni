"""Application settings."""

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
