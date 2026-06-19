"""Configuration helpers for TrustLayer AI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings with Streamlit Community Cloud friendly defaults."""

    app_name: str = "TrustLayer AI"
    model_name: str = "gpt-4o-mini"
    max_file_size_bytes: int = 200000
    agent_retry_attempts: int = 2
    openai_api_key: Optional[str] = None


def get_config() -> AppConfig:
    """Return immutable app configuration."""

    return AppConfig(
        model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        max_file_size_bytes=int(os.getenv("MAX_FILE_SIZE_BYTES", "200000")),
        agent_retry_attempts=int(os.getenv("AGENT_RETRY_ATTEMPTS", "2")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
