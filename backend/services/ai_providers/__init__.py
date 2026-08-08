"""
AI Providers module.

Factory for creating AI provider instances based on configuration.
"""
from typing import Dict, Any
from core.config import settings

from .base import AIProvider
from .copilot_provider import CopilotProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider


_provider_cache: Dict[str, AIProvider] = {}


def create_ai_provider() -> AIProvider:
    """
    Create an AI provider instance based on current configuration.
    
    Returns:
        AIProvider: Configured AI provider instance
        
    Raises:
        ValueError: If the configured provider is not supported
    """
    provider_name = settings.ai_provider.lower()
    
    if provider_name in _provider_cache:
        return _provider_cache[provider_name]

    if provider_name == "copilot":
        config = {
            "model": settings.copilot_model,
            "github_token": settings.copilot_github_token,
            "base_directory": settings.copilot_home,
            "timeout": settings.generation_timeout,
        }
        provider = CopilotProvider(config)

    elif provider_name == "openai":
        config = {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
        }
        provider = OpenAIProvider(config)
    
    elif provider_name == "ollama":
        config = {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model,
        }
        provider = OllamaProvider(config)
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")

    _provider_cache[provider_name] = provider
    return provider


async def close_ai_providers() -> None:
    """Close cached provider clients during application shutdown."""
    providers = list(_provider_cache.values())
    _provider_cache.clear()
    for provider in providers:
        await provider.close()


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all available AI providers.
    
    Returns:
        dict: Provider information keyed by provider name
    """
    return {
        "copilot": {
            "name": "GitHub Copilot SDK",
            "description": "Uses the signed-in GitHub Copilot subscription via the Copilot SDK",
            "requires_api_key": False,
            "requires_copilot_subscription": True,
            "supports_streaming": True,
            "model_selection": settings.copilot_model,
        },
        "openai": {
            "name": "OpenAI",
            "description": "Direct OpenAI API access",
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
    "CopilotProvider",
    "OpenAIProvider", 
    "OllamaProvider",
    "create_ai_provider",
    "close_ai_providers",
    "get_available_providers"
]
