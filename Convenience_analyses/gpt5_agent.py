#
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Maxim Strekolovskiy
#
"""
GPT-5 agent for the `Convenience_analyses` (UX) microservice.

This module calls the OpenAI Responses API and returns a plain-text UX report.
It can optionally include screenshots (as image inputs) when provided.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from .settings import settings

logger = logging.getLogger(__name__)


class GPT5APIError(Exception):
    """Raised when the OpenAI Responses API request fails."""


class ConvenienceAnalysisAgent:
    """UX/Usability analysis agent."""

    SYSTEM_PROMPT = (
        "You are ConvenienceAnalysisAgent, an expert in UX/UI and usability auditing. "
        "You will receive structured signals (navigation, accessibility, responsive heuristics) "
        "and optionally screenshots for multiple viewports. "
        "Produce a detailed PLAIN TEXT report in English (NOT JSON). "
        "Include: scores (0-100) per category, key issues with evidence, and a prioritized action plan."
    )

    def __init__(self) -> None:
        self.timeout = httpx.Timeout(
            settings.REQUEST_TIMEOUT,
            read=settings.REQUEST_TIMEOUT,
            write=settings.REQUEST_TIMEOUT,
            connect=min(30, settings.REQUEST_TIMEOUT),
        )

    @staticmethod
    def _normalize_images(images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize various screenshot formats to Responses API image inputs.
        Supported inputs:
        - Chat-style: {"type":"image_url","image_url":{"url":"data:image/png;base64,...","detail":"high"}}
        - Responses-style: {"type":"input_image","image_url":"..."}
        """
        normalized: List[Dict[str, Any]] = []
        for item in images:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "input_image":
                normalized.append(item)
                continue
            if item.get("type") == "image_url":
                image_url = item.get("image_url", {})
                url = image_url.get("url") if isinstance(image_url, dict) else image_url
                if url:
                    normalized.append({"type": "input_image", "image_url": url})
        return normalized

    async def analyze(
        self, data: Dict[str, Any], images: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze UX/usability for a website.
        Returns:
            dict: {"analysis": "<plain text>"}
        """
        content: List[Dict[str, Any]] = [
            {
                "type": "input_text",
                "text": (
                    "Analyze the UX/usability of the website based on the following data.\n\n"
                    f"{json.dumps(data, ensure_ascii=False, indent=2)}"
                ),
            }
        ]
        if images:
            content.extend(self._normalize_images(images))
        payload: Dict[str, Any] = {
            "model": settings.OPENAI_MODEL,
            "input": [{"role": "user", "content": content}],
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
        if proxy_url:
            mounts = {
                "http://": httpx.AsyncHTTPTransport(proxy=proxy_url),
                "https://": httpx.AsyncHTTPTransport(proxy=proxy_url),
            }
            client_kwargs: Dict[str, Any] = {"timeout": self.timeout, "mounts": mounts}
        else:
            client_kwargs = {"timeout": self.timeout}
        async with httpx.AsyncClient(**client_kwargs) as client:
            resp = await client.post(
                f"{settings.OPENAI_BASE_URL.rstrip('/')}/responses",
                json=payload,
                headers=headers,
            )
        if resp.status_code != 200:
            raise GPT5APIError(f"OpenAI API returned {resp.status_code}: {resp.text}")
        return {"analysis": self._extract_text(resp.json())}

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
