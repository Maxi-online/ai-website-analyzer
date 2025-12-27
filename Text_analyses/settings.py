# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Application settings for the `Text_analyses` microservice.

GitHub-safe policy:

- Never hardcode secrets in source code.

- All credentials must come from environment variables.

"""

from __future__ import annotations

import os
from typing import Any


class Settings:
    """Centralized environment-based configuration (no secrets in defaults)."""

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    # GPT-5 Responses API parameters
    OPENAI_VERBOSITY: str = os.getenv("OPENAI_VERBOSITY", "medium")
    OPENAI_REASONING_EFFORT: str = os.getenv("OPENAI_REASONING_EFFORT", "medium")
    OPENAI_TOOL_CHOICE: str = os.getenv("OPENAI_TOOL_CHOICE", "auto")
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
    TEXT_SERVICE_PORT: int = int(os.getenv("TEXT_SERVICE_PORT", "8002"))
    # Analysis settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "600"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    @classmethod
    def validate_required_keys(cls) -> list[str]:
        """Return a list of missing keys required to call OpenAI APIs."""
        missing: list[str] = []
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        return missing

    @classmethod
    def get_proxy_url(cls) -> str:
        """Build a proxy URL usable by httpx, or return an empty string."""
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
        Docs:
        - https://platform.openai.com/docs/guides/responses-tools
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


settings = Settings()
