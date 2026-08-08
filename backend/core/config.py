"""Configuration management for the AI Novel App backend."""

from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # Database
    database_url: str = "sqlite:///./ai_novel_app.db"

    # AI Provider Configuration
    # Copilot is the default because it can use an existing GitHub Copilot
    # subscription without storing a model API key in this application.
    ai_provider: str = "copilot"  # copilot, openai, or ollama

    # GitHub Copilot SDK Configuration
    # "auto" is compatible with plans that require automatic model selection
    # (including Copilot Student). Leave the token unset for local CLI auth.
    copilot_model: str = "auto"
    copilot_github_token: Optional[str] = None
    copilot_home: Optional[str] = None

    # Optional OpenAI API fallback
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # Application Settings
    debug: bool = False
    secret_key: Optional[str] = None
    cors_origins: List[str] = ["http://localhost:3000"]

    # Generation Settings
    max_chapters_per_story: int = 50
    default_chapter_length: int = 2000
    generation_timeout: int = 300

    # Novel complexity setting
    novel_complexity: str = "standard"  # simple, standard, complex, literary

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Novel Writing App"
    version: str = "1.1.0"


# Global settings instance
settings = Settings()
