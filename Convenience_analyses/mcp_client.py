# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""HTTP client for Bright Data MCP (optional helper for the UX service)."""

import logging
from typing import Any, Dict, Optional

import httpx

from .settings import settings

logger = logging.getLogger(__name__)


class BrightDataMCPError(Exception):
    """Bright Data MCP interaction error."""


class BrightDataMCPClient:
    """Async client for calling Bright Data MCP tools."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self.api_token = api_token or settings.BRIGHTDATA_API_TOKEN
        self.base_url = (base_url or settings.BRIGHTDATA_MCP_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.BRIGHTDATA_MCP_TIMEOUT
        if not self.api_token or not self.base_url:
            raise BrightDataMCPError("Bright Data MCP credentials are not configured")

    async def call_tool(
        self, tool: str, args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call an MCP tool and return its JSON result."""
        url = (
            f"{self.base_url}/tools/{tool}"
            if self.base_url.endswith("/mcp")
            else f"{self.base_url}/mcp/tools/{tool}"
        )
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {"args": args or {}}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
            except httpx.HTTPError as exc:
                logger.exception("Bright Data MCP request failed")
                raise BrightDataMCPError(
                    f"HTTP error calling Bright Data MCP: {exc}"
                ) from exc
        if response.status_code != 200:
            logger.error(
                "Bright Data MCP error",
                extra={
                    "tool": tool,
                    "status_code": response.status_code,
                    "body": response.text,
                },
            )
            raise BrightDataMCPError(
                f"Bright Data MCP returned status {response.status_code}: {response.text}"
            )
        return response.json()

    async def scrape_as_markdown(self, url: str) -> Dict[str, Any]:
        """Return page content as Markdown."""
        return await self.call_tool("scrape_as_markdown", {"url": url})

    async def capture_screenshot(
        self, url: str, viewport: str = "desktop"
    ) -> Dict[str, Any]:
        """Return a screenshot for a given viewport."""
        return await self.call_tool("screenshot", {"url": url, "viewport": viewport})
