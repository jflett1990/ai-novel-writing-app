"""
Abstract base class for AI providers.

This defines the interface that all AI providers must implement,
allowing seamless switching between OpenAI, Ollama, and future providers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass


@dataclass
class GenerationParams:
    """Parameters for text generation."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[list] = None

    @classmethod
    def for_creative_writing(cls) -> 'GenerationParams':
        """
        Parameters optimized for creative, original writing.

        Returns:
            GenerationParams: Settings that promote creativity and reduce repetition
        """
        return cls(
            temperature=0.7,  # Moderate creativity for better control
            top_p=0.9,        # Slightly more focused than default
            frequency_penalty=0.6,  # Strong penalty against repetitive phrases
            presence_penalty=0.4,   # Strong penalty to encourage topic diversity
        )

    @classmethod
    def for_character_creation(cls) -> 'GenerationParams':
        """
        Parameters optimized for character generation.

        Returns:
            GenerationParams: Settings that promote diverse, original characters
        """
        return cls(
            temperature=0.85,  # High creativity for unique characters
            top_p=0.85,        # Allow for unexpected traits
            frequency_penalty=0.4,  # Avoid character clichés
            presence_penalty=0.3,   # Encourage diverse backgrounds
        )

    @classmethod
    def for_plot_development(cls) -> 'GenerationParams':
        """
        Parameters optimized for plot and outline generation.

        Returns:
            GenerationParams: Settings that balance creativity with coherence
        """
        return cls(
            temperature=0.75,  # Moderate creativity for coherent plots
            top_p=0.9,         # Focused but creative
            frequency_penalty=0.25, # Reduce plot clichés
            presence_penalty=0.15,  # Some topic diversity
        )


@dataclass
class GenerationResult:
    """Result from text generation."""
    text: str
    tokens_used: int
    model_used: str
    finish_reason: str
    metadata: Dict[str, Any] = None


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    This interface allows the application to work with different AI services
    (OpenAI, Ollama, etc.) through a common API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the AI provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> GenerationResult:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: The input prompt for text generation
            params: Generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            GenerationResult containing the generated text and metadata
            
        Raises:
            AIProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_text_stream(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate text with streaming response.
        
        Args:
            prompt: The input prompt for text generation
            params: Generation parameters
            
        Yields:
            str: Chunks of generated text as they become available
            
        Raises:
            AIProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the AI provider is available and responsive.
        
        Returns:
            bool: True if the provider is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            dict: Model information (name, context_length, etc.)
        """
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text.
        
        This is a rough estimation. Providers can override with more accurate methods.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            int: Estimated number of tokens
        """
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    
    def __init__(self, message: str, provider: str, error_code: Optional[str] = None):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        super().__init__(f"[{provider}] {message}")


class AIProviderUnavailableError(AIProviderError):
    """Raised when an AI provider is unavailable."""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Raised when rate limits are exceeded."""
    pass


class AIProviderAuthError(AIProviderError):
    """Raised when authentication fails."""
    pass
