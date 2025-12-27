# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

GPT-5 agent for the `Text_analyses` microservice.

This module calls the OpenAI Responses API and extracts a plain-text analysis.

"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import httpx

from .settings import settings


class GPT5APIError(Exception):
    """Raised when the OpenAI Responses API request fails."""


class TextAnalysisAgent:
    """Analyzes textual content signals and produces a report."""

    SYSTEM_PROMPT = (
        "You are TextAnalysisAgent. Analyze readability, keyword density, structure, "
        "and overall clarity of the provided webpage data. "
        "Return a detailed PLAIN TEXT report in English (NOT JSON). "
        "Include metrics, issues, and actionable recommendations."
    )

    async def analyze(self, payload_data: Dict[str, Any]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": settings.OPENAI_MODEL,
            "input": json.dumps(payload_data, ensure_ascii=False),
            "instructions": self.SYSTEM_PROMPT,
            "reasoning": {"effort": settings.OPENAI_REASONING_EFFORT},
            "text": {"verbosity": settings.OPENAI_VERBOSITY},
            "store": False,
        }
        tools = settings.get_builtin_tools()
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = settings.OPENAI_TOOL_CHOICE
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
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
                f"OpenAI API returned {response.status_code}: {response.text}"
            )
        return {"analysis": self._extract_text(response.json())}

    @staticmethod
    def _extract_text(response_payload: Dict[str, Any]) -> str:
        segments: List[str] = []
        for output_item in response_payload.get("output", []):
            if output_item.get("type") != "message":
                continue
            for content in output_item.get("content", []):
                if content.get("type") == "output_text":
                    segments.append(content.get("text", ""))
        if not segments:
            raise GPT5APIError("OpenAI Responses API returned empty output")
        return "".join(segments).strip()


async def analyze_with_agent(
    agent: TextAnalysisAgent, payload_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Compatibility helper to invoke the agent."""
    return await agent.analyze(payload_data)
