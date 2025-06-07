"""
AI Providers module.

Factory for creating AI provider instances based on configuration.
"""
from typing import Dict, Any
from core.config import settings

from .base import AIProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider


def create_ai_provider() -> AIProvider:
    """
    Create an AI provider instance based on current configuration.
    
    Returns:
        AIProvider: Configured AI provider instance
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider_name = settings.ai_provider.lower()
    
    if provider_name == "openai":
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        return OpenAIProvider(config)
    
    elif provider_name == "ollama":
        config = {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        }
        return OllamaProvider(config)
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all available AI providers.
    
    Returns:
        dict: Provider information keyed by provider name
    """
    return {
        "openai": {
            "name": "OpenAI",
            "description": "OpenAI's GPT models (GPT-4, GPT-3.5-turbo)",
            "requires_api_key": True,
            "supports_streaming": True,
            "cost": "paid",
        },
        "ollama": {
            "name": "Ollama",
            "description": "Local LLM inference with Ollama",
            "requires_api_key": False,
            "supports_streaming": True,
            "cost": "free",
            "requires_local_setup": True,
        }
    }


# Export main classes and functions
__all__ = [
    "AIProvider",
    "OpenAIProvider", 
    "OllamaProvider",
    "create_ai_provider",
    "get_available_providers"
]
