"""
Ollama provider implementation.

Implements the AIProvider interface using Ollama's local API.
Ollama provides an OpenAI-compatible endpoint for local LLM inference.
"""
import json
from typing import Dict, Any, Optional, AsyncGenerator
import httpx

from .base import (
    AIProvider, 
    GenerationParams, 
    GenerationResult,
    AIProviderError,
    AIProviderUnavailableError,
    AIProviderRateLimitError,
    AIProviderAuthError
)


class OllamaProvider(AIProvider):
    """
    Ollama provider implementation.
    
    Uses Ollama's local API for text generation with local models.
    Ollama provides an OpenAI-compatible /v1/completions endpoint.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.
        
        Args:
            config: Configuration dict with 'base_url' and 'model'
        """
        super().__init__(config)
        
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama2")
        
        # Ensure base_url doesn't end with slash
        self.base_url = self.base_url.rstrip("/")
        
        # Ollama API endpoints
        self.chat_url = f"{self.base_url}/api/chat"
        self.generate_url = f"{self.base_url}/api/generate"
        self.models_url = f"{self.base_url}/api/tags"
    
    async def generate_text(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> GenerationResult:
        """Generate text using Ollama's API."""
        if params is None:
            params = GenerationParams()
        
        try:
            # Prepare the request for Ollama's chat API
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {
                    "temperature": params.temperature,
                    "top_p": params.top_p,
                }
            }
            
            if params.max_tokens:
                request_data["options"]["num_predict"] = params.max_tokens
            
            if params.stop_sequences:
                request_data["options"]["stop"] = params.stop_sequences
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(self.chat_url, json=request_data)
                if response.status_code != 200:
                    raise AIProviderError(
                        f"Ollama API error: {response.status_code} - {response.text}",
                        "ollama"
                    )

                result = response.json()

                # Extract the generated text
                generated_text = result.get("message", {}).get("content", "")

                # Ollama doesn't provide exact token counts, so we estimate
                estimated_tokens = self.estimate_tokens(prompt + generated_text)

                return GenerationResult(
                    text=generated_text,
                    tokens_used=estimated_tokens,
                    model_used=self.model,
                    finish_reason=result.get("done_reason", "stop"),
                    metadata={
                        "eval_count": result.get("eval_count", 0),
                        "eval_duration": result.get("eval_duration", 0),
                        "load_duration": result.get("load_duration", 0),
                        "prompt_eval_count": result.get("prompt_eval_count", 0),
                    }
                )
                    
        except AIProviderError:
            raise
        except httpx.TimeoutException:
            raise AIProviderError("Request timeout", "ollama", "timeout")
        except httpx.HTTPError as e:
            raise AIProviderUnavailableError(f"Connection error: {str(e)}", "ollama")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}", "ollama")
    
    async def generate_text_stream(
        self, 
        prompt: str, 
        params: Optional[GenerationParams] = None
    ) -> AsyncGenerator[str, None]:
        """Generate text with streaming response."""
        if params is None:
            params = GenerationParams()
        
        try:
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "options": {
                    "temperature": params.temperature,
                    "top_p": params.top_p,
                }
            }
            
            if params.max_tokens:
                request_data["options"]["num_predict"] = params.max_tokens
            
            if params.stop_sequences:
                request_data["options"]["stop"] = params.stop_sequences
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream("POST", self.chat_url, json=request_data) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise AIProviderError(
                            f"Ollama API error: {response.status_code} - {error_text.decode('utf-8', errors='replace')}",
                            "ollama"
                        )

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk_data = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        content = chunk_data.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk_data.get("done", False):
                            break

        except AIProviderError:
            raise
        except httpx.TimeoutException:
            raise AIProviderError("Request timeout", "ollama", "timeout")
        except httpx.HTTPError as e:
            raise AIProviderUnavailableError(f"Connection error: {str(e)}", "ollama")
        except Exception as e:
            raise AIProviderError(f"Unexpected error: {str(e)}", "ollama")
    
    async def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.models_url)
                return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current Ollama model."""
        return {
            "name": self.model,
            "provider": "ollama",
            "type": "chat",
            "base_url": self.base_url,
            # Context length varies by model, would need to query Ollama for specifics
            "context_length": 4096,  # Default assumption
        }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for local models.
        
        This is a rough estimate since different models may have different tokenizers.
        """
        # Conservative estimate: ~3 characters per token for most models
        return len(text) // 3
