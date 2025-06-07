"""
OpenAI provider implementation.

Implements the AIProvider interface using OpenAI's API.
"""
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
import openai
from openai import AsyncOpenAI

from .base import (
    AIProvider, 
    GenerationParams, 
    GenerationResult,
    AIProviderError,
    AIProviderUnavailableError,
    AIProviderRateLimitError,
    AIProviderAuthError
)


class OpenAIProvider(AIProvider):
    """
    OpenAI provider implementation.
    
    Uses OpenAI's API for text generation with models like GPT-4, GPT-3.5-turbo.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Configuration dict with 'api_key' and 'model'
        """
        super().__init__(config)
        
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")
        self.organization = config.get("organization")
        
        if not self.api_key:
            raise AIProviderError("OpenAI API key is required", "openai")
        
        # Initialize async client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization
        )
    
    async def generate_text(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> GenerationResult:
        """Generate text using OpenAI's API."""
        if params is None:
            params = GenerationParams()
        
        try:
            # Prepare the request
            messages = [{"role": "user", "content": prompt}]
            
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": params.temperature,
                "top_p": params.top_p,
                "frequency_penalty": params.frequency_penalty,
                "presence_penalty": params.presence_penalty,
            }
            
            if params.max_tokens:
                request_params["max_tokens"] = params.max_tokens
            
            if params.stop_sequences:
                request_params["stop"] = params.stop_sequences
            
            # Make the API call
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract the result
            choice = response.choices[0]
            generated_text = choice.message.content
            
            return GenerationResult(
                text=generated_text,
                tokens_used=response.usage.total_tokens,
                model_used=response.model,
                finish_reason=choice.finish_reason,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            )
            
        except openai.RateLimitError as e:
            raise AIProviderRateLimitError(str(e), "openai", "rate_limit")
        except openai.AuthenticationError as e:
            raise AIProviderAuthError(str(e), "openai", "auth_error")
        except openai.APIConnectionError as e:
            raise AIProviderUnavailableError(str(e), "openai", "connection_error")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}", "openai")
    
    async def generate_text_stream(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming response."""
        if params is None:
            params = GenerationParams()
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": params.temperature,
                "top_p": params.top_p,
                "frequency_penalty": params.frequency_penalty,
                "presence_penalty": params.presence_penalty,
                "stream": True,
            }
            
            if params.max_tokens:
                request_params["max_tokens"] = params.max_tokens
            
            if params.stop_sequences:
                request_params["stop"] = params.stop_sequences
            
            # Stream the response
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except openai.RateLimitError as e:
            raise AIProviderRateLimitError(str(e), "openai", "rate_limit")
        except openai.AuthenticationError as e:
            raise AIProviderAuthError(str(e), "openai", "auth_error")
        except openai.APIConnectionError as e:
            raise AIProviderUnavailableError(str(e), "openai", "connection_error")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}", "openai")
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            # Make a minimal API call to test availability
            await self.client.models.list()
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current OpenAI model."""
        model_info = {
            "name": self.model,
            "provider": "openai",
            "type": "chat",
        }
        
        # Add known context lengths for common models
        context_lengths = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
        }
        
        if self.model in context_lengths:
            model_info["context_length"] = context_lengths[self.model]
        
        return model_info
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens using OpenAI's approximation.
        
        For more accuracy, could use tiktoken library, but this is sufficient for estimates.
        """
        # OpenAI's rough estimate: ~4 characters per token
        return len(text) // 4
