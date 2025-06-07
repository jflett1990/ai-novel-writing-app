"""
Configuration management for the AI Novel App backend.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./ai_novel_app.db"
    
    # AI Provider Configuration
    ai_provider: str = "openai"  # openai or ollama
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Application Settings
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    cors_origins: List[str] = ["*"]
    
    # Generation Settings
    max_chapters_per_story: int = 50
    default_chapter_length: int = 2000
    generation_timeout: int = 300

    # Novel complexity setting
    novel_complexity: str = "standard"  # simple, standard, complex, literary
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Novel Writing App"
    version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
