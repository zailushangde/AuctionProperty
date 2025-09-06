"""Configuration management for the auction platform."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:[YOUR-PASSWORD]@db.hwyuvjamgcawjcpsitrj.supabase.co:5432/postgres",
        description="PostgreSQL database URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL for Celery broker"
    )
    
    # SHAB API
    shab_base_url: str = Field(
        default="https://amtsblattportal.ch/api/v1",
        description="SHAB API base URL"
    )
    
    # Application
    app_name: str = Field(default="Swiss Auction Platform", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Scheduler
    fetch_interval_hours: int = Field(
        default=24,
        description="Hours between SHAB data fetches"
    )
    
    # Optional: Elasticsearch
    elasticsearch_url: Optional[str] = Field(
        default=None,
        description="Elasticsearch URL for full-text search"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
