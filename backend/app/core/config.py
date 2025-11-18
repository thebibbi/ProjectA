"""
Application configuration management.

Uses Pydantic Settings for environment variable parsing and validation.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes are automatically loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application metadata
    api_title: str = Field(
        default="Safety Graph Twin API",
        description="API title displayed in documentation",
    )
    api_version: str = Field(
        default="0.1.0",
        description="API version",
    )
    api_description: str = Field(
        default="Backend API for ISO 26262 Safety Knowledge Graph",
        description="API description",
    )

    # Server configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the API server to",
    )
    api_port: int = Field(
        default=8000,
        description="Port to bind the API server to",
        ge=1,
        le=65535,
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload on code changes (development only)",
    )

    # Neo4j database configuration
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j connection URI",
    )
    neo4j_user: str = Field(
        default="neo4j",
        description="Neo4j username",
    )
    neo4j_password: str = Field(
        default="safetygraph123",
        description="Neo4j password",
    )
    neo4j_database: str = Field(
        default="neo4j",
        description="Neo4j database name",
    )
    neo4j_max_connection_lifetime: int = Field(
        default=3600,
        description="Max connection lifetime in seconds",
        ge=60,
    )
    neo4j_max_connection_pool_size: int = Field(
        default=50,
        description="Max connection pool size",
        ge=1,
        le=1000,
    )
    neo4j_connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1,
    )

    # CORS configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )
    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods for CORS",
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers for CORS",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: str = Field(
        default="text",
        description="Log format: text or json",
    )

    # Security configuration (for future use)
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT tokens (future use)",
    )
    algorithm: str = Field(
        default="HS256",
        description="Algorithm for JWT tokens (future use)",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes (future use)",
        ge=1,
    )

    # Rate limiting (for future use)
    rate_limit_per_minute: int = Field(
        default=100,
        description="API rate limit per minute per IP (future use)",
        ge=1,
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got {v}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = ["text", "json"]
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"log_format must be one of {valid_formats}, got {v}")
        return v_lower

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def neo4j_connection_uri(self) -> str:
        """Get Neo4j connection URI with credentials."""
        return self.neo4j_uri

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.reload

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.is_development


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Cached Settings instance

    The settings are cached to avoid reloading from environment on every call.
    Use this function throughout the application to access settings.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
