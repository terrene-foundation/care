"""Application configuration loaded from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    provider: str = os.getenv("CARE_LLM_PROVIDER", "anthropic")
    model: str = os.getenv("CARE_LLM_MODEL", "claude-sonnet-4-6")
    base_url: str | None = os.getenv("CARE_LLM_BASE_URL")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


@dataclass(frozen=True)
class ServerConfig:
    host: str = os.getenv("CARE_API_HOST", "127.0.0.1")
    port: int = int(os.getenv("CARE_API_PORT", "8000"))
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv(
            "CARE_CORS_ORIGINS", "http://localhost:3000"
        ).split(",")
    )


@dataclass(frozen=True)
class WhisperConfig:
    model: str = os.getenv("CARE_WHISPER_MODEL", "base")
    device: str = os.getenv("CARE_WHISPER_DEVICE", "cpu")


@dataclass(frozen=True)
class AppConfig:
    mode: str = os.getenv("CARE_MODE", "selfhosted")
    llm: LLMConfig = field(default_factory=LLMConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)


def load_config() -> AppConfig:
    return AppConfig()
