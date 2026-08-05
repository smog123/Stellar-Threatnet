from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"  # development | test | production
    PROJECT_NAME: str = "Stellar ThreatNet"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = (
        "Open threat intelligence infrastructure for the Stellar ecosystem. "
        "Wallet, domain and token reputation lookups, incident feed, community "
        "reports with moderation, and an AI threat assistant."
    )

    # --- Security ---
    SECRET_KEY: str = "SUPER_SECRET_STELLAR_THREATNET_KEY_CHANGE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # --- Databases ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://threatnet_user:threatnet_pass@localhost:5432/stellar_threatnet"
    )
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Caching ---
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 900  # 15 minutes

    # --- Rate limiting ---
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "120/minute"

    # --- AI ---
    AI_PROVIDER: str = "mock"  # mock | openai | anthropic | ollama
    OPENAI_API_KEY: str = ""

    # --- Reputation scoring (see docs/THREAT_MODEL.md) ---
    BASE_REPUTATION_SCORE: int = 80
    VERIFIED_BOOST: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def _fail_fast_on_weak_secret(self):
        """Refuse to run with the shipped default or short signing key in production."""
        if self.ENV == "production" and (
            len(self.SECRET_KEY) < 32 or "CHANGE_IN_PRODUCTION" in self.SECRET_KEY
        ):
            raise ValueError(
                "SECRET_KEY must be a unique secret >= 32 bytes when ENV=production"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
