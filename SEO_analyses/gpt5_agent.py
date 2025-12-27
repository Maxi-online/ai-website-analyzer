# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Maxim Strekolovskiy

"""
GPT-5 agent for the `SEO_analyses` service.

This module calls the OpenAI Responses API and extracts plain text output.
Docs:
- https://platform.openai.com/docs/guides/migrate-to-responses
"""

import json
from typing import Any, Dict, List

import httpx

from .settings import settings


class GPT5APIError(Exception):
    """Raised when the OpenAI Responses API request fails."""

    pass


class SEOAnalysisAgent:
    """SEO agent for search optimization analysis."""

    SYSTEM_PROMPT = (
        "You are SEOAnalysisAgent. Analyse provided on-page data, meta tags, structure, links, Core Web Vitals. "
        "Provide a detailed SEO analysis with scoring, issues, and recommendations. "
        "Write your analysis in a clear, structured format. "
        "Provide analysis as PLAIN TEXT in English, NOT JSON."
    )

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze payload via the OpenAI Responses API.
        Returns:
            dict: {"analysis": "<plain text>"}
        """
        payload = {
            "model": settings.OPENAI_MODEL,
            "input": json.dumps(data, ensure_ascii=False),
            "instructions": self.SYSTEM_PROMPT,
            "reasoning": {"effort": settings.OPENAI_REASONING_EFFORT},
            "text": {"verbosity": settings.OPENAI_VERBOSITY},
            "store": False,
        }
        # Tools (built from env toggles in settings)
        tools = settings.get_builtin_tools()
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = settings.OPENAI_TOOL_CHOICE
        # Optional grammar (controlled by OPENAI_GRAMMAR_ENABLED in settings)
        grammar_config = settings.get_grammar_config()
        if grammar_config:
            payload["grammar"] = grammar_config
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        # Optional proxy via httpx transports
        proxy_url = settings.get_proxy_url()
        timeout = httpx.Timeout(
            settings.REQUEST_TIMEOUT,
            read=settings.REQUEST_TIMEOUT,
            write=settings.REQUEST_TIMEOUT,
            connect=settings.REQUEST_TIMEOUT,
        )
        if proxy_url:
            mounts = {
                "http://": httpx.AsyncHTTPTransport(proxy=proxy_url),
                "https://": httpx.AsyncHTTPTransport(proxy=proxy_url),
            }
            client_kwargs = {"timeout": timeout, "mounts": mounts}
        else:
            client_kwargs = {"timeout": timeout}
        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.post(
                f"{settings.OPENAI_BASE_URL.rstrip('/')}/responses",
                json=payload,
                headers=headers,
            )
        if response.status_code != 200:
            raise GPT5APIError(
                f"GPT-5 API returned {response.status_code}: {response.text}"
            )
        text_output = self._extract_text(response.json())
        return {"analysis": text_output}

    @staticmethod
    def _extract_text(response_payload: Dict[str, Any]) -> str:
        """
        Extract plain text from a Responses API response payload.
        Expected format:
        {"output":[{"type":"message","content":[{"type":"output_text","text":"..."}]}]}
        """
        segments: List[str] = []
        for output_item in response_payload.get("output", []):
            if output_item.get("type") == "message":
                for content in output_item.get("content", []):
                    if content.get("type") == "output_text":
                        segments.append(content.get("text", ""))
        if not segments:
            raise GPT5APIError("GPT-5 API returned empty output")
        return "".join(segments).strip()


async def analyze_with_agent(
    agent: SEOAnalysisAgent, data: Dict[str, Any]
) -> Dict[str, Any]:
    """Compatibility helper to invoke the agent."""
    return await agent.analyze(data)
