"""
Application Configuration

Manages all configuration settings using Pydantic Settings.
Environment variables are loaded from .env file.
"""
from typing import List, Any, Optional
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in:
    1. .env file (development)
    2. System environment (production)
    3. Docker environment (container)
    """

    # ========================================
    # Application Settings
    # ========================================
    PROJECT_NAME: str = "Life Tracker API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # ========================================
    # Server Settings
    # ========================================
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ========================================
    # Database Settings
    # ========================================
    DATABASE_URL: str

    # Example: postgresql://user:password@localhost:5432/dbname
    # Docker: postgresql://postgres:password@db:5432/mood_tracker

    @property
    def database_url_async(self) -> str:
        """
        Async database URL for SQLAlchemy.
        Converts postgresql:// to postgresql+asyncpg://
        """
        if "postgresql://" in self.DATABASE_URL and "asyncpg" not in self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL

    @property
    def database_url_sync(self) -> str:
        """
        Sync database URL for Alembic migrations.
        Converts postgresql+asyncpg:// to postgresql://
        """
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("+asyncpg", "")

    # ========================================
    # Security Settings
    # ========================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Token expiry (in seconds)
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 2592000  # 30 days

    # Pepper for refresh token hashing
    # Pepper for token hashing (optional)
    TOKEN_PEPPER: str = ""

    @field_validator("TOKEN_PEPPER")
    @classmethod
    def validate_pepper(cls, v: str) -> str:
        """Validate pepper is set (optional but recommended)"""
        if not v:
            import warnings
            warnings.warn(
                "TOKEN_PEPPER not set. "
                "Consider setting it for additional security."
            )
        return v

    # ========================================
    # CORS Settings
    # ========================================
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        """
        Parse CORS origins from comma-separated string or list.

        Supports:
        - List: ["http://localhost:3000", "http://localhost:8080"]
        - String: "http://localhost:3000,http://localhost:8080"
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    # ========================================
    # AI Service Settings
    # ========================================
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    # ========================================
    # Logging Settings
    # ========================================
    LOG_LEVEL: str = "INFO"
    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

    # ========================================
    # Rate Limiting (Future - placeholder)
    # ========================================
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # ========================================
    # Pydantic Config
    # ========================================
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields in .env
    )


# Create global settings instance
settings = Settings()