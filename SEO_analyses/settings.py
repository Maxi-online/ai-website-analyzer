# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Application settings for the `SEO_analyses` microservice.

GitHub-safe policy:

- Never hardcode secrets in source code.

- All credentials must come from environment variables.

This module also provides helpers for the OpenAI Responses API tools payload.

"""

from __future__ import annotations

import os
from typing import Any


class Settings:
    """Centralized environment-based configuration (no secrets in defaults)."""

    # Yandex Wordstat API (legacy)
    YANDEX_URL: str = os.getenv(
        "YANDEX_URL", "https://api-sandbox.direct.yandex.ru/v4/json/"
    )
    YANDEX_TOKEN: str = os.getenv("YANDEX_TOKEN", "")
    YANDEX_USERNAME: str = os.getenv("YANDEX_USERNAME", "")
    # Yandex API (modern)
    YANDEX_WORDSTAT_TOKEN: str = os.getenv("YANDEX_WORDSTAT_TOKEN", "")
    YANDEX_CLOUD_API_KEY: str = os.getenv("YANDEX_CLOUD_API_KEY", "")
    YANDEX_CLIENT_ID: str = os.getenv("YANDEX_CLIENT_ID", "")
    YANDEX_CLIENT_SECRET: str = os.getenv("YANDEX_CLIENT_SECRET", "")
    # Yandex API URLs
    YANDEX_SUGGEST_URL: str = os.getenv(
        "YANDEX_SUGGEST_URL", "https://suggest.yandex.ru/suggest-ya.cgi"
    )
    YANDEX_DIRECT_URL: str = os.getenv(
        "YANDEX_DIRECT_URL", "https://api.direct.yandex.ru/v4/json/"
    )
    YANDEX_CLOUD_URL: str = os.getenv(
        "YANDEX_CLOUD_URL", "https://cloud-api.yandex.net/v1/"
    )
    # GTmetrix API (optional)
    GTMETRIX_API_KEY: str = os.getenv("GTMETRIX_API_KEY", "")
    GTMETRIX_BASE_URL: str = os.getenv(
        "GTMETRIX_BASE_URL", "https://gtmetrix.com/api/2.0"
    )
    GTMETRIX_DEFAULT_LOCATION: str = os.getenv(
        "GTMETRIX_DEFAULT_LOCATION", "1"
    )  # Default location ID
    GTMETRIX_DEFAULT_BROWSER: str = os.getenv(
        "GTMETRIX_DEFAULT_BROWSER", "3"
    )  # Default browser ID
    GTMETRIX_DEFAULT_REPORT_TYPE: str = os.getenv(
        "GTMETRIX_DEFAULT_REPORT_TYPE", "lighthouse"
    )  # lighthouse, legacy, lighthouse,legacy, none
    GTMETRIX_DEFAULT_RETENTION: int = int(os.getenv("GTMETRIX_DEFAULT_RETENTION", "1"))
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    # GPT-5 Responses API parameters
    OPENAI_VERBOSITY: str = os.getenv("OPENAI_VERBOSITY", "medium")
    OPENAI_REASONING_EFFORT: str = os.getenv("OPENAI_REASONING_EFFORT", "medium")
    # Legacy generation parameters (kept for compatibility; Responses prefers reasoning/verbosity)
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
    OPENAI_TOP_P: float = float(os.getenv("OPENAI_TOP_P", "1.0"))
    OPENAI_FREQUENCY_PENALTY: float = float(
        os.getenv("OPENAI_FREQUENCY_PENALTY", "0.0")
    )
    OPENAI_PRESENCE_PENALTY: float = float(os.getenv("OPENAI_PRESENCE_PENALTY", "0.0"))
    OPENAI_STOP_SEQUENCES: str = os.getenv("OPENAI_STOP_SEQUENCES", "")
    # Built-in tools toggles
    OPENAI_ENABLE_WEB_SEARCH: bool = (
        os.getenv("OPENAI_ENABLE_WEB_SEARCH", "true").lower() == "true"
    )
    OPENAI_ENABLE_CODE_INTERPRETER: bool = (
        os.getenv("OPENAI_ENABLE_CODE_INTERPRETER", "true").lower() == "true"
    )
    OPENAI_ENABLE_PYTHON_EXEC: bool = (
        os.getenv("OPENAI_ENABLE_PYTHON_EXEC", "false").lower() == "true"
    )
    OPENAI_TOOL_CHOICE: str = os.getenv("OPENAI_TOOL_CHOICE", "auto")
    # Remote MCP servers (optional)
    OPENAI_ENABLE_BRIGHTDATA_MCP: bool = (
        os.getenv("OPENAI_ENABLE_BRIGHTDATA_MCP", "false").lower() == "true"
    )
    # Grammar
    OPENAI_GRAMMAR_ENABLED: bool = (
        os.getenv("OPENAI_GRAMMAR_ENABLED", "false").lower() == "true"
    )
    # Proxy settings (optional)
    PROXY_ENABLED: bool = os.getenv("PROXY_ENABLED", "false").lower() == "true"
    PROXY_HOST: str = os.getenv("PROXY_HOST", "")
    PROXY_PORT: int = int(os.getenv("PROXY_PORT", "0"))
    PROXY_USERNAME: str = os.getenv("PROXY_USERNAME", "")
    PROXY_PASSWORD: str = os.getenv("PROXY_PASSWORD", "")
    PROXY_TYPE: str = os.getenv("PROXY_TYPE", "http")  # http or socks5
    # Bright Data MCP (optional)
    BRIGHTDATA_API_TOKEN: str = os.getenv("BRIGHTDATA_API_TOKEN", "")
    BRIGHTDATA_MCP_BASE_URL: str = os.getenv("BRIGHTDATA_MCP_BASE_URL", "")
    BRIGHTDATA_MCP_TIMEOUT: int = int(os.getenv("BRIGHTDATA_MCP_TIMEOUT", "60"))
    # Service ports
    SEO_SERVICE_PORT: int = int(os.getenv("SEO_SERVICE_PORT", "8001"))
    TEXT_SERVICE_PORT: int = int(os.getenv("TEXT_SERVICE_PORT", "8002"))
    CONVENIENCE_SERVICE_PORT: int = int(os.getenv("CONVENIENCE_SERVICE_PORT", "8003"))
    SENIOR_SERVICE_PORT: int = int(os.getenv("SENIOR_SERVICE_PORT", "8004"))
    # Analysis settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "600"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    # Screenshot settings (used by Convenience service, kept here for compatibility)
    SCREENSHOT_WIDTH: int = int(os.getenv("SCREENSHOT_WIDTH", "1920"))
    SCREENSHOT_HEIGHT: int = int(os.getenv("SCREENSHOT_HEIGHT", "1080"))

    @classmethod
    def validate_required_keys(cls) -> list[str]:
        """
        Validate required credentials for this service.
        This method does not raise. It returns a list of missing/invalid keys so
        callers can decide whether to error out, warn, or run in degraded mode.
        """
        missing_keys: list[str] = []
        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        return missing_keys

    @classmethod
    def get_optional_keys(cls) -> dict[str, bool]:
        """Return a dict of optional keys/features and whether they are configured."""
        return {
            "GTMETRIX_API_KEY": bool(cls.GTMETRIX_API_KEY),
            "YANDEX_WORDSTAT_TOKEN": bool(cls.YANDEX_WORDSTAT_TOKEN),
            "YANDEX_CLOUD_API_KEY": bool(cls.YANDEX_CLOUD_API_KEY),
            "YANDEX_CLIENT_ID": bool(cls.YANDEX_CLIENT_ID),
            "YANDEX_CLIENT_SECRET": bool(cls.YANDEX_CLIENT_SECRET),
            "BRIGHTDATA_API_TOKEN": bool(cls.BRIGHTDATA_API_TOKEN),
            "PROXY_ENABLED": bool(cls.get_proxy_url()),
        }

    @classmethod
    def get_proxy_url(cls) -> str:
        """
        Build a proxy URL from environment variables.
        Returns:
            str: Proxy URL usable by httpx `proxy=` parameter, or empty string.
        Behavior:
        - If `PROXY_ENABLED` is false -> returns "".
        - If `PROXY_HOST`/`PROXY_PORT` are missing -> returns "".
        - If username/password are missing -> returns a URL without auth.
        """
        if not cls.PROXY_ENABLED:
            return ""
        if not (cls.PROXY_HOST and cls.PROXY_PORT):
            return ""
        auth = ""
        if cls.PROXY_USERNAME and cls.PROXY_PASSWORD:
            auth = f"{cls.PROXY_USERNAME}:{cls.PROXY_PASSWORD}@"
        return f"{cls.PROXY_TYPE}://{auth}{cls.PROXY_HOST}:{cls.PROXY_PORT}"

    @classmethod
    def get_builtin_tools(cls) -> list[dict[str, Any]]:
        """
        Build the `tools` list for OpenAI Responses API requests.
        Official docs:
        - https://platform.openai.com/docs/guides/responses-tools
        Built-in tools (OpenAI-hosted) examples:
        - {"type": "web_search"}
        - {"type": "code_interpreter", "container": {"type": "auto"}}
        - {"type": "file_search"}
        - {"type": "image_generation"}
        - {"type": "computer_use"}
        Remote MCP servers (external tools) example:
        - {
            "type": "mcp",
            "server_label": "brightdata",
            "server_url": "https://mcp.brightdata.com/mcp",
            "authorization": "Bearer <token>",
            "require_approval": "never"
          }
        """
        tools: list[dict[str, Any]] = []
        if cls.OPENAI_ENABLE_WEB_SEARCH:
            tools.append({"type": "web_search"})
        if cls.OPENAI_ENABLE_CODE_INTERPRETER:
            tools.append({"type": "code_interpreter", "container": {"type": "auto"}})
        if (
            cls.OPENAI_ENABLE_BRIGHTDATA_MCP
            and cls.BRIGHTDATA_API_TOKEN
            and cls.BRIGHTDATA_MCP_BASE_URL
        ):
            tools.append(
                {
                    "type": "mcp",
                    "server_label": "brightdata",
                    "server_url": cls.BRIGHTDATA_MCP_BASE_URL,
                    "authorization": f"Bearer {cls.BRIGHTDATA_API_TOKEN}",
                    "require_approval": "never",
                }
            )
        # Optional custom function tool (normally code_interpreter is enough)
        if cls.OPENAI_ENABLE_PYTHON_EXEC:
            tools.append(
                {
                    "type": "function",
                    "name": "python_execute",
                    "description": "Execute Python code for data analysis and transformations.",
                    "parameters": {
                        "type": "object",
                        "properties": {"code": {"type": "string"}},
                        "required": ["code"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
            )
        return tools

    @classmethod
    def get_allowed_tools_list(cls) -> list[dict[str, Any]]:
        """Deprecated compatibility alias for `get_builtin_tools()`."""
        return cls.get_builtin_tools()

    @classmethod
    def get_grammar_config(cls) -> dict[str, Any]:
        """
        Return an optional grammar configuration for the Responses API.
        Notes:
        - Grammar is disabled by default (`OPENAI_GRAMMAR_ENABLED=false`).
        - If enabled, we provide a small CFG example that forces a predictable
          sectioned report format.
        """
        if not cls.OPENAI_GRAMMAR_ENABLED:
            return {}
        return {
            "type": "CFG",
            "rules": {
                "start": ["<intro>\n\n<analysis>\n\n<conclusion>"],
                "intro": ["Analysis:\n<text>"],
                "analysis": ["Detailed analysis:\n<text>"],
                "conclusion": ["Conclusions and recommendations:\n<text>"],
                "text": [
                    "<sentence>",
                    "<sentence> <sentence>",
                    "<sentence> <sentence> <sentence>",
                ],
                "sentence": ["[A-Z][^.!?]+[.!?]"],
            },
        }

    @classmethod
    def has_brightdata_credentials(cls) -> bool:
        """Return True if Bright Data MCP is configured."""
        return bool(cls.BRIGHTDATA_API_TOKEN and cls.BRIGHTDATA_MCP_BASE_URL)


settings = Settings()
