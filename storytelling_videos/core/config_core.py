from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide configuration.
    """

    # Core App Info
    PROJECT_NAME: str = Field(default="StoryTelling", description="Project name")
    ENVIRONMENT: str = Field(
        default="dev", description="App environment: dev | qa | staging | production"
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode for development")

    # Database
    MONGODB_URI: str = Field(..., description="MongoDB connection string")
    MONGODB_DB: str = Field(default="mongo_sync", description="Mongo database name")

    # OpenRouter
    OPENROUTER_API: str = Field(..., description="OpenRouter API String")

    # --- Logging / Monitoring ---
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Easier for Docker/Kubernetes environments
        extra="ignore",  # Ignore unexpected env vars
    )

    @field_validator("MONGODB_URI")
    @classmethod
    def ensure_mongo_uri(cls, v: str) -> str:
        if not (v.startswith("mongodb://") or v.startswith("mongodb+srv://")):
            raise ValueError("MONGODB_URI must start with mongodb:// or mongodb+srv://")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
