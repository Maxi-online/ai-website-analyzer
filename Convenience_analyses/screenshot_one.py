# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

ScreenshotOne API client for capturing website screenshots.

Docs:
- https://screenshotone.com/docs/

This helper returns screenshots as base64 and can also format them as `image_url`

objects suitable for image inputs.

"""

from __future__ import annotations

import base64
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests

from .settings import settings

logger = logging.getLogger(__name__)


class ScreenshotOneClient:
    """Minimal ScreenshotOne API client."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )

    def _build_url(self, params: Dict[str, Any]) -> str:
        base_url = settings.SCREENSHOTONE_API_URL.rstrip("?")
        query = urlencode(params)
        return f"{base_url}?{query}"

    def capture_screenshot(
        self,
        url: str,
        *,
        viewport_width: int,
        viewport_height: int,
        full_page: bool,
        device_scale_factor: int,
        image_format: str,
        quality: int,
        block_ads: bool,
        block_cookie_banners: bool,
        wait_for_load: bool,
        delay_ms: int,
    ) -> Optional[str]:
        """
        Capture a screenshot for a given URL and return it as base64.
        Returns:
            str | None: Base64-encoded image bytes, or None on error.
        """
        if not settings.SCREENSHOTONE_ACCESS_KEY:
            logger.warning(
                "SCREENSHOTONE_ACCESS_KEY is not configured; skipping screenshots"
            )
            return None
        params: Dict[str, Any] = {
            "access_key": settings.SCREENSHOTONE_ACCESS_KEY,
            "url": url,
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
            "full_page": "true" if full_page else "false",
            "device_scale_factor": device_scale_factor,
            "format": image_format,
            "quality": quality,
            "block_ads": "true" if block_ads else "false",
            "block_cookie_banners": "true" if block_cookie_banners else "false",
            "wait_for": "load" if wait_for_load else "domcontentloaded",
            "delay": delay_ms,
        }
        signed_url = self._build_url(params)
        try:
            logger.info("Capturing screenshot via ScreenshotOne: %s", url)
            response = self.session.get(signed_url, timeout=60)
            if response.status_code != 200:
                logger.error(
                    "ScreenshotOne API error: %s - %s",
                    response.status_code,
                    response.text,
                )
                return None
            return base64.b64encode(response.content).decode("ascii")
        except Exception as exc:
            logger.error("Screenshot capture failed for %s: %s", url, exc)
            return None

    async def capture_multiple_screenshots(
        self, *, url: str, devices: List[str]
    ) -> Dict[str, Any]:
        """
        Capture screenshots for multiple device profiles.
        Returns:
            dict: {
              "status": "success"|"error",
              "vision_data": [<image_url objects>],
              "screenshots_info": {device: "..."},
              "message": "..."
            }
        """
        profiles: Dict[str, Dict[str, Any]] = {
            "desktop": {
                "label": "Desktop",
                "viewport_width": 1366,
                "viewport_height": 768,
                "full_page": True,
                "device_scale_factor": 1,
            },
            "mobile": {
                "label": "Mobile",
                "viewport_width": 390,
                "viewport_height": 844,
                "full_page": False,
                "device_scale_factor": 2,
            },
            "tablet": {
                "label": "Tablet",
                "viewport_width": 820,
                "viewport_height": 1180,
                "full_page": True,
                "device_scale_factor": 2,
            },
        }
        screenshots_info: Dict[str, str] = {}
        vision_data: List[Dict[str, Any]] = []
        # The network call is synchronous (requests). For simplicity and reliability,
        # we keep it sequential here; the UX service already runs async overall.
        for device in devices:
            config = profiles.get(device)
            if not config:
                screenshots_info[device] = "Unsupported device profile"
                continue
            b64 = self.capture_screenshot(
                url,
                viewport_width=config["viewport_width"],
                viewport_height=config["viewport_height"],
                full_page=config["full_page"],
                device_scale_factor=config["device_scale_factor"],
                image_format="png",
                quality=85,
                block_ads=True,
                block_cookie_banners=True,
                wait_for_load=True,
                delay_ms=1000,
            )
            if not b64:
                screenshots_info[device] = (
                    f"Failed to capture screenshot for {config['label']}"
                )
                continue
            vision_data.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                        "detail": "high",
                    },
                    "metadata": {"device": device, "label": config["label"]},
                }
            )
            screenshots_info[device] = f"Captured {config['label']} screenshot"
        status = "success" if vision_data else "error"
        return {
            "status": status,
            "vision_data": vision_data,
            "screenshots_info": screenshots_info,
            "message": f"Captured {len(vision_data)} screenshots out of {len(devices)}",
        }
