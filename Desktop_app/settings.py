# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Settings for the desktop UI application.

GitHub-safe policy:

- Never hardcode secrets in source code.

- Read all credentials from environment variables.

"""

from __future__ import annotations

import os


class Settings:
    """Desktop app configuration (ports, OpenAI, and optional proxy)."""

    # Microservice ports (defaults match docker-compose.yml)
    SEO_SERVICE_PORT: int = int(os.getenv("SEO_SERVICE_PORT", "8001"))
    TEXT_SERVICE_PORT: int = int(os.getenv("TEXT_SERVICE_PORT", "8002"))
    CONVENIENCE_SERVICE_PORT: int = int(os.getenv("CONVENIENCE_SERVICE_PORT", "8003"))
    SENIOR_SERVICE_PORT: int = int(os.getenv("SENIOR_SERVICE_PORT", "8004"))
    # OpenAI (desktop app may call microservices only, but we keep for parity)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    # Proxy (optional)
    PROXY_ENABLED: bool = os.getenv("PROXY_ENABLED", "false").lower() == "true"
    PROXY_HOST: str = os.getenv("PROXY_HOST", "")
    PROXY_PORT: int = int(os.getenv("PROXY_PORT", "0"))
    PROXY_USERNAME: str = os.getenv("PROXY_USERNAME", "")
    PROXY_PASSWORD: str = os.getenv("PROXY_PASSWORD", "")
    PROXY_TYPE: str = os.getenv("PROXY_TYPE", "http")  # http or socks5

    @classmethod
    def get_proxy_url(cls) -> str:
        """Build a proxy URL usable by requests/httpx, or return an empty string."""
        if not cls.PROXY_ENABLED:
            return ""
        if not (cls.PROXY_HOST and cls.PROXY_PORT):
            return ""
        auth = ""
        if cls.PROXY_USERNAME and cls.PROXY_PASSWORD:
            auth = f"{cls.PROXY_USERNAME}:{cls.PROXY_PASSWORD}@"
        return f"{cls.PROXY_TYPE}://{auth}{cls.PROXY_HOST}:{cls.PROXY_PORT}"


settings = Settings()
