from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).with_name(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openweather_api_key: str = Field(default="")
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    joke_api_base_url: str = "https://v2.jokeapi.dev"
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    app_api_key: str = "change_me"
    max_summary_text_length: int = 5000


settings = Settings()
