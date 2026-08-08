"""GitHub Copilot SDK provider.

The provider runs the SDK in ``empty`` mode and exposes no tools.  Novel prompts
therefore get text generation without ambient filesystem, shell, MCP, skill, or
agent capabilities.
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from copilot import CopilotClient
from copilot.rpc import PermissionDecisionReject
from copilot.session_events import (
    AssistantMessageData,
    AssistantMessageDeltaData,
    AssistantUsageData,
    SessionErrorData,
    SessionIdleData,
)

from .base import (
    AIProvider,
    AIProviderAuthError,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderUnavailableError,
    GenerationParams,
    GenerationResult,
)


SYSTEM_MESSAGE = """You are the prose-generation engine for a novel-writing application.
Follow the user's fiction-writing request closely and return only the requested
writing or structured writing output. Do not use tools or perform external actions.
"""


def _reject_permission(_request: Any, _invocation: Dict[str, Any]):
    """Fail closed if the runtime ever asks to execute a tool."""
    return PermissionDecisionReject(feedback="Tool use is disabled for novel generation.")


class CopilotProvider(AIProvider):
    """Text generation backed by the GitHub Copilot SDK."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = config.get("model") or "auto"
        self.github_token = config.get("github_token")
        # Empty mode deliberately has no ambient Copilot configuration/tools, but
        # the SDK still requires an explicit data directory.  Using the normal
        # Copilot home preserves the user's existing local sign-in by default.
        self.base_directory = config.get("base_directory") or str(Path.home() / ".copilot")
        self.timeout = float(config.get("timeout") or 300)
        self._client: Optional[CopilotClient] = None
        self._client_lock = asyncio.Lock()

    async def _get_client(self) -> CopilotClient:
        async with self._client_lock:
            if self._client is None:
                options: Dict[str, Any] = {
                    "mode": "empty",
                    "base_directory": self.base_directory,
                    "use_logged_in_user": not bool(self.github_token),
                }
                if self.github_token:
                    options["github_token"] = self.github_token
                self._client = CopilotClient(**options)

            await self._client.start()
            return self._client

    def _session_options(self, *, streaming: bool) -> Dict[str, Any]:
        return {
            "model": self.model,
            "streaming": streaming,
            "tools": [],
            "available_tools": [],
            "on_permission_request": _reject_permission,
            "system_message": {"mode": "append", "content": SYSTEM_MESSAGE},
            "infinite_sessions": {"enabled": False},
            "memory": {"enabled": False},
            "enable_session_store": False,
            "enable_skills": False,
            "enable_config_discovery": False,
            "skip_custom_instructions": True,
        }

    @staticmethod
    def _provider_error(exc: Exception) -> AIProviderError:
        message = str(exc) or exc.__class__.__name__
        lowered = message.lower()
        if any(marker in lowered for marker in ("401", "403", "auth", "login", "credential")):
            return AIProviderAuthError(message, "copilot", "auth_error")
        if "429" in lowered or "rate limit" in lowered or "quota" in lowered:
            return AIProviderRateLimitError(message, "copilot", "rate_limit")
        if "timeout" in lowered or "timed out" in lowered or "connection" in lowered:
            return AIProviderUnavailableError(message, "copilot", "unavailable")
        return AIProviderError(message, "copilot")

    async def generate_text(
        self,
        prompt: str,
        params: Optional[GenerationParams] = None,
    ) -> GenerationResult:
        del params  # Copilot subscription model selection owns sampling controls.

        input_tokens = 0
        output_tokens = 0
        model_used = self.model
        finish_reason = "stop"

        def capture_usage(event: Any) -> None:
            nonlocal input_tokens, output_tokens, model_used, finish_reason
            if isinstance(event.data, AssistantUsageData):
                input_tokens += event.data.input_tokens or 0
                output_tokens += event.data.output_tokens or 0
                model_used = event.data.model or model_used
                finish_reason = event.data.finish_reason or finish_reason

        try:
            client = await self._get_client()
            session = await client.create_session(**self._session_options(streaming=False))
            async with session:
                unsubscribe = session.on(capture_usage)
                try:
                    response = await session.send_and_wait(prompt, timeout=self.timeout)
                finally:
                    unsubscribe()

            if response is None or not isinstance(response.data, AssistantMessageData):
                raise AIProviderError("Copilot returned no assistant message", "copilot")

            data = response.data
            model_used = data.model or model_used
            if not output_tokens:
                output_tokens = data.output_tokens or 0

            return GenerationResult(
                text=data.content,
                tokens_used=input_tokens + output_tokens,
                model_used=model_used,
                finish_reason=finish_reason,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "sampling_controls": "managed_by_copilot",
                },
            )
        except AIProviderError:
            raise
        except Exception as exc:
            raise self._provider_error(exc) from exc

    async def generate_text_stream(
        self,
        prompt: str,
        params: Optional[GenerationParams] = None,
    ) -> AsyncGenerator[str, None]:
        del params
        queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

        def on_event(event: Any) -> None:
            if isinstance(event.data, AssistantMessageDeltaData):
                if event.data.delta_content:
                    queue.put_nowait(("chunk", event.data.delta_content))
            elif isinstance(event.data, SessionErrorData):
                queue.put_nowait(("error", event.data.message))
            elif isinstance(event.data, SessionIdleData):
                queue.put_nowait(("done", None))

        try:
            client = await self._get_client()
            session = await client.create_session(**self._session_options(streaming=True))
            async with session:
                unsubscribe = session.on(on_event)
                try:
                    await session.send(prompt)
                    while True:
                        kind, payload = await asyncio.wait_for(queue.get(), timeout=self.timeout)
                        if kind == "chunk":
                            yield payload
                        elif kind == "error":
                            raise AIProviderError(str(payload), "copilot")
                        else:
                            break
                finally:
                    unsubscribe()
        except AIProviderError:
            raise
        except Exception as exc:
            raise self._provider_error(exc) from exc

    async def is_available(self) -> bool:
        try:
            client = await self._get_client()
            models = await client.list_models()
            return bool(models)
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model,
            "provider": "copilot",
            "type": "chat",
            "selection": "automatic" if self.model == "auto" else "configured",
        }

    async def close(self) -> None:
        async with self._client_lock:
            if self._client is not None:
                try:
                    await self._client.stop()
                except Exception:
                    # A runtime that failed during startup may already have a
                    # closed pipe. Shutdown must stay idempotent for app teardown.
                    pass
                finally:
                    self._client = None
