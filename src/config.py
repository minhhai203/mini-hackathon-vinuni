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
        model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
