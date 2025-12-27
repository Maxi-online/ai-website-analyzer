# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Senior (aggregator) service orchestration.

This module:

- Calls SEO/Text/Convenience microservices in parallel.

- Aggregates their outputs into a single payload.

- Sends the payload to the GPT-5 Responses API via `SeniorAnalysisAgent`.

"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .gpt5_agent import SeniorAnalysisAgent
from .settings import settings


@dataclass(frozen=True)
class ServiceEndpoints:

    seo: str
    text: str
    convenience: str


class SeniorAnalyzer:
    """Orchestrates microservices and produces a final comparative report."""

    def __init__(self) -> None:
        self.agent = SeniorAnalysisAgent()

    @staticmethod
    def _get_endpoints() -> ServiceEndpoints:
        """
        Resolve microservice base URLs depending on environment.
        In Docker Compose, the service names are resolvable hostnames.
        Locally, services are assumed to run on localhost.
        """
        docker_env = os.getenv("DOCKER_ENV", "false").lower() == "true"
        if docker_env:
            return ServiceEndpoints(
                seo=f"http://seo-service:{settings.SEO_SERVICE_PORT}",
                text=f"http://text-service:{settings.TEXT_SERVICE_PORT}",
                convenience=f"http://convenience-service:{settings.CONVENIENCE_SERVICE_PORT}",
            )
        return ServiceEndpoints(
            seo=f"http://localhost:{settings.SEO_SERVICE_PORT}",
            text=f"http://localhost:{settings.TEXT_SERVICE_PORT}",
            convenience=f"http://localhost:{settings.CONVENIENCE_SERVICE_PORT}",
        )

    @staticmethod
    async def _post_json_for_text(
        url: str, payload: dict[str, Any], timeout_s: int
    ) -> str:
        async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_s)) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.text

    async def _analyze_site_raw(self, site_url: str) -> dict[str, Any]:
        endpoints = self._get_endpoints()
        seo_url = f"{endpoints.seo}/seo_analysis"
        text_url = f"{endpoints.text}/text_analysis"
        convenience_url = f"{endpoints.convenience}/convenience_analysis"
        timeout_s = settings.REQUEST_TIMEOUT
        seo_task = self._post_json_for_text(seo_url, {"url": site_url}, timeout_s)
        text_task = self._post_json_for_text(text_url, {"url": site_url}, timeout_s)
        convenience_task = self._post_json_for_text(
            convenience_url, {"url": site_url}, timeout_s
        )
        seo_text, text_text, convenience_text = await asyncio.gather(
            seo_task, text_task, convenience_task
        )
        return {
            "url": site_url,
            "seo_analysis": seo_text,
            "text_analysis": text_text,
            "convenience_analysis": convenience_text,
        }

    async def compare_sites(self, site1_url: str, site2_url: str) -> str:
        """
        Compare two sites and return a plain-text report (English).
        """
        site1_raw, site2_raw = await asyncio.gather(
            self._analyze_site_raw(site1_url), self._analyze_site_raw(site2_url)
        )
        payload: dict[str, Any] = {
            "mode": "compare",
            "site1": site1_raw,
            "site2": site2_raw,
            "timestamp": time.time(),
        }
        result = await self.agent.analyze(payload)
        return result.get("analysis", "")

    async def analyze_single_site(self, url: str) -> dict[str, Any]:
        """
        Analyze a single site and return a JSON-friendly payload with a GPT-5 report.
        """
        raw = await self._analyze_site_raw(url)
        payload: dict[str, Any] = {
            "mode": "single",
            "site": raw,
            "timestamp": time.time(),
        }
        gpt = await self.agent.analyze(payload)
        return {
            "url": url,
            "raw_data": raw,
            "gpt5_analysis": gpt,
            "timestamp": payload["timestamp"],
        }

    async def generate_recommendations(
        self, site_url: str, competitor_url: str
    ) -> dict[str, Any]:
        """
        Generate an improvement plan for `site_url` using `competitor_url` as a benchmark.
        """
        analysis_text = await self.compare_sites(site_url, competitor_url)
        return {
            "site_url": site_url,
            "competitor_url": competitor_url,
            "analysis_text": analysis_text,
            "timestamp": time.time(),
        }

    async def get_service_status(self) -> dict[str, Any]:
        """
        Check the availability of dependent microservices.
        """
        endpoints = self._get_endpoints()
        services = {
            "seo_service": endpoints.seo,
            "text_service": endpoints.text,
            "convenience_service": endpoints.convenience,
        }
        results: dict[str, Any] = {}
        overall_ok = True
        async with httpx.AsyncClient(timeout=httpx.Timeout(10)) as client:
            for name, base_url in services.items():
                start = time.perf_counter()
                try:
                    r = await client.get(f"{base_url}/")
                    ok = r.status_code == 200
                except Exception as exc:
                    ok = False
                    results[name] = {
                        "status": "offline",
                        "url": base_url,
                        "error": str(exc),
                    }
                else:
                    dt = time.perf_counter() - start
                    results[name] = {
                        "status": "online" if ok else "degraded",
                        "url": base_url,
                        "response_time_s": round(dt, 3),
                    }
                overall_ok = overall_ok and ok
        return {
            "overall_status": "online" if overall_ok else "degraded",
            "services": results,
            "timestamp": time.time(),
        }
