# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""
Convenience (UX) analyzer using a GPT-5 agent.

This module:
- collects basic UX heuristics (navigation, accessibility, responsive design)
- optionally captures screenshots via ScreenshotOne
- sends the aggregated payload to GPT-5 for a final plain-text report
"""

import asyncio
import logging
import re
from typing import Any, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .gpt5_agent import ConvenienceAnalysisAgent
from .screenshot_one import ScreenshotOneClient
from .settings import settings

logger = logging.getLogger(__name__)


class ConvenienceAnalyzer:
    """High-level UX analyzer for websites.
    It collects deterministic heuristics and asks GPT-5 to produce a report.
    """

    def __init__(self):
        """Initialize the analyzer and HTTP session."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }
        )
        self.convenience_agent = ConvenienceAnalysisAgent()
        self.screenshot_client = ScreenshotOneClient()

    async def analyze_url(self, url: str) -> str:
        """Run a full UX analysis for a URL and return a GPT-5 plain-text report."""
        try:
            loop = asyncio.get_running_loop()
            convenience_data = {
                "url": url,
                "navigation": await loop.run_in_executor(
                    None, lambda: self._analyze_navigation(url)
                ),
                "accessibility": await loop.run_in_executor(
                    None, lambda: self._analyze_accessibility(url)
                ),
                "responsive_design": await loop.run_in_executor(
                    None, lambda: self._analyze_responsive_design(url)
                ),
            }
            screenshots_result = (
                await self.screenshot_client.capture_multiple_screenshots(
                    url=url,
                    devices=["desktop", "mobile", "tablet"],
                )
            )
            vision_data = None
            if (
                screenshots_result["status"] == "success"
                and screenshots_result["vision_data"]
            ):
                vision_data = screenshots_result["vision_data"]
                convenience_data["design_screenshots"] = screenshots_result[
                    "screenshots_info"
                ]
            else:
                convenience_data["design_screenshots"] = {
                    "error": "Screenshots are not available"
                }
            gpt5_analysis = await self.convenience_agent.analyze(
                convenience_data, images=vision_data
            )
            return gpt5_analysis.get("analysis", str(gpt5_analysis))
        except Exception as exc:
            logger.error("Convenience analysis failed for %s: %s", url, exc)
            return f"Convenience analysis failed for {url}: {exc}"

    def _analyze_navigation(self, url: str) -> Dict[str, Any]:
        """
        Analyze basic navigation signals.
        """
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
            nav_elements = soup.find_all(["nav", "header"])
            menu_items = soup.find_all(["a", "button"])
            has_main_menu = len(nav_elements) > 0
            has_breadcrumbs = bool(soup.find(class_=re.compile(r"breadcrumb", re.I)))
            has_search = bool(
                soup.find(["input", "form"], attrs={"type": "search"})
                or soup.find(
                    ["input", "form"], attrs={"name": re.compile(r"search|query", re.I)}
                )
            )
            internal_links = 0
            external_links = 0
            parsed_url = urlparse(url)
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.startswith("http"):
                    link_domain = urlparse(href).netloc
                    if link_domain == parsed_url.netloc:
                        internal_links += 1
                    else:
                        external_links += 1
                elif href and not href.startswith("#"):
                    internal_links += 1
            return {
                "has_main_menu": has_main_menu,
                "has_breadcrumbs": has_breadcrumbs,
                "has_search": has_search,
                "menu_items_count": len(menu_items),
                "internal_links": internal_links,
                "external_links": external_links,
                "navigation_depth": min(3, len(nav_elements)),
            }
        except Exception as exc:
            logger.error("Navigation analysis failed: %s", exc)
            return {
                "error": str(exc),
                "has_main_menu": False,
                "has_breadcrumbs": False,
                "has_search": False,
            }

    def _analyze_accessibility(self, url: str) -> Dict[str, Any]:
        """
        Analyze basic accessibility signals.
        """
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
            images = soup.find_all("img")
            images_with_alt = sum(1 for img in images if img.get("alt"))
            aria_elements = soup.find_all(
                attrs=lambda x: x and any(k.startswith("aria-") for k in x.keys())
            )
            semantic_elements = soup.find_all(
                ["header", "nav", "main", "article", "section", "aside", "footer"]
            )
            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            h1_count = len(soup.find_all("h1"))
            form_inputs = soup.find_all(["input", "select", "textarea"])
            inputs_with_labels = sum(
                1
                for inp in form_inputs
                if inp.get("id") and soup.find("label", attrs={"for": inp.get("id")})
            )
            has_skip_links = bool(
                soup.find("a", string=re.compile(r"skip|skip to content", re.I))
            )
            return {
                "images_total": len(images),
                "images_with_alt": images_with_alt,
                "alt_coverage": round(
                    (images_with_alt / len(images) * 100) if images else 100, 2
                ),
                "aria_elements": len(aria_elements),
                "semantic_html5": len(semantic_elements) > 0,
                "semantic_elements_count": len(semantic_elements),
                "headings_count": len(headings),
                "h1_count": h1_count,
                "proper_h1": h1_count == 1,
                "form_inputs": len(form_inputs),
                "labeled_inputs": inputs_with_labels,
                "label_coverage": round(
                    (
                        (inputs_with_labels / len(form_inputs) * 100)
                        if form_inputs
                        else 100
                    ),
                    2,
                ),
                "has_skip_links": has_skip_links,
            }
        except Exception as exc:
            logger.error("Accessibility analysis failed: %s", exc)
            return {
                "error": str(exc),
                "images_with_alt": 0,
                "aria_elements": 0,
                "semantic_html5": False,
            }

    def _analyze_responsive_design(self, url: str) -> Dict[str, Any]:
        """
        Analyze basic responsive design signals.
        """
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
            viewport = soup.find("meta", attrs={"name": "viewport"})
            has_viewport = viewport is not None
            viewport_content = viewport.get("content", "") if viewport else ""
            style_tags = soup.find_all("style")
            has_media_queries = False
            for style in style_tags:
                if style.string and "@media" in style.string:
                    has_media_queries = True
                    break
            css_content = " ".join([style.string or "" for style in style_tags])
            uses_relative_units = any(
                unit in css_content for unit in ["em", "rem", "%", "vw", "vh"]
            )
            responsive_images = soup.find_all("img", srcset=True)
            picture_elements = soup.find_all("picture")
            uses_flexbox = "flex" in css_content or "display: flex" in str(soup)
            uses_grid = "grid" in css_content or "display: grid" in str(soup)
            return {
                "has_viewport": has_viewport,
                "viewport_content": viewport_content,
                "has_media_queries": has_media_queries,
                "uses_relative_units": uses_relative_units,
                "responsive_images": len(responsive_images),
                "picture_elements": len(picture_elements),
                "uses_flexbox": uses_flexbox,
                "uses_grid": uses_grid,
                "css_framework_detected": self._detect_css_framework(soup, css_content),
            }
        except Exception as exc:
            logger.error("Responsive design analysis failed: %s", exc)
            return {
                "error": str(exc),
                "has_viewport": False,
                "has_media_queries": False,
                "uses_relative_units": False,
            }

    def _detect_css_framework(self, soup: BeautifulSoup, css_content: str) -> str:
        """
        Detect a common CSS framework (best-effort).
        """
        frameworks = {
            "bootstrap": ["bootstrap", "col-md", "col-sm", "col-lg", "container-fluid"],
            "tailwind": ["tailwind", "tw-", "text-gray", "bg-blue", "flex-col"],
            "bulma": ["bulma", "columns", "column is-", "hero", "section"],
            "foundation": ["foundation", "row", "columns small-", "callout"],
            "materialize": ["materialize", "waves-effect", "card-panel", "collection"],
            "semantic-ui": ["semantic", "ui container", "ui grid", "ui menu"],
        }
        page_html = str(soup)
        for framework, indicators in frameworks.items():
            if any(
                indicator in page_html.lower() or indicator in css_content.lower()
                for indicator in indicators
            ):
                return framework
        return "custom"
