"""LLM provider abstraction — supports Anthropic, OpenAI, and Ollama."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from care.config import LLMConfig


class LLMProvider:
    """Unified LLM interface that streams responses."""

    def __init__(self, config: LLMConfig) -> None:
        self._config = config
        self._client = httpx.AsyncClient(timeout=120.0)

    async def stream(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream text tokens from the LLM."""
        if self._config.provider == "anthropic":
            async for token in self._stream_anthropic(messages, system, temperature):
                yield token
        elif self._config.provider == "openai":
            async for token in self._stream_openai(messages, system, temperature):
                yield token
        elif self._config.provider == "ollama":
            async for token in self._stream_ollama(messages, system, temperature):
                yield token
        else:
            raise ValueError(f"Unknown LLM provider: {self._config.provider}")

    async def complete(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Get a complete (non-streaming) response. Used for structured extraction."""
        tokens: list[str] = []
        async for token in self.stream(messages, system, temperature):
            tokens.append(token)
        return "".join(tokens)

    async def extract_json(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        retries: int = 2,
    ) -> dict[str, Any]:
        """Get a JSON response from the LLM. Retries on parse failure."""
        json_system = (system or "") + (
            "\n\nYou MUST respond with valid JSON only. No markdown, no explanation, "
            "no code fences. Just the JSON object."
        )
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            response = await self.complete(
                messages, system=json_system, temperature=0.1
            )
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[: cleaned.rfind("```")]
            try:
                return json.loads(cleaned.strip())
            except json.JSONDecodeError as e:
                last_error = e
                if attempt < retries:
                    # Add the failed response context for the retry
                    messages = messages + [
                        {"role": "assistant", "content": response},
                        {
                            "role": "user",
                            "content": "That was not valid JSON. Please respond with ONLY a valid JSON object.",
                        },
                    ]
        # All retries exhausted — return empty dict rather than crashing the session
        return {"_extraction_failed": True, "_error": str(last_error)}

    # ── Anthropic ────────────────────────────────────────────

    async def _stream_anthropic(
        self,
        messages: list[dict[str, str]],
        system: str | None,
        temperature: float,
    ) -> AsyncIterator[str]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self._config.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body: dict[str, Any] = {
            "model": self._config.model,
            "max_tokens": 4096,
            "temperature": temperature,
            "stream": True,
            "messages": messages,
        }
        if system:
            body["system"] = system

        async with self._client.stream("POST", url, headers=headers, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                event = json.loads(data)
                if event.get("type") == "content_block_delta":
                    delta = event.get("delta", {})
                    if text := delta.get("text"):
                        yield text

    # ── OpenAI-compatible (OpenAI, vLLM) ─────────────────────

    async def _stream_openai(
        self,
        messages: list[dict[str, str]],
        system: str | None,
        temperature: float,
    ) -> AsyncIterator[str]:
        base_url = self._config.base_url or "https://api.openai.com/v1"
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._config.openai_api_key or ''}",
            "Content-Type": "application/json",
        }
        all_messages = messages.copy()
        if system:
            all_messages.insert(0, {"role": "system", "content": system})

        body = {
            "model": self._config.model,
            "temperature": temperature,
            "stream": True,
            "messages": all_messages,
        }

        async with self._client.stream("POST", url, headers=headers, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                event = json.loads(data)
                choices = event.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    if content := delta.get("content"):
                        yield content

    # ── Ollama ───────────────────────────────────────────────

    async def _stream_ollama(
        self,
        messages: list[dict[str, str]],
        system: str | None,
        temperature: float,
    ) -> AsyncIterator[str]:
        base_url = self._config.base_url or "http://localhost:11434"
        url = f"{base_url}/api/chat"
        all_messages = messages.copy()
        if system:
            all_messages.insert(0, {"role": "system", "content": system})

        body = {
            "model": self._config.model,
            "messages": all_messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        async with self._client.stream("POST", url, json=body) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                event = json.loads(line)
                if message := event.get("message"):
                    if content := message.get("content"):
                        yield content

    async def close(self) -> None:
        await self._client.aclose()
