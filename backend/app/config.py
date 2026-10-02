"""Application configuration."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    app_name: str = "Ten at a Time"
    environment: str = "production"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/tenatatime.db"

    # Auth (single-user for now, designed for multi-user later)
    auth_password: str = ""

    # Push notifications
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_subject: str = "mailto:ten@werewolfhowl.com"

    # CORS
    cors_origins: str = "*"

    class Config:
        env_file = ".env"
        env_prefix = ""

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
