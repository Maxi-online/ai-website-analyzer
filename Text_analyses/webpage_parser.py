# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Web page parser for extracting textual content and basic metadata.

This module is used by the Text Analyses service for:

- parsing pages

- extracting text by CSS selector

- comparing pages

"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class WebPageParser:
    """Parse web pages and extract content/metadata."""

    CONTENT_SELECTORS: List[str] = [
        "main",
        "article",
        "[role='main']",
        ".content",
        "#content",
        ".main",
        "#main",
    ]
    EXCLUDE_SELECTORS: List[str] = [
        "nav",
        "header",
        "footer",
        "aside",
        "script",
        "style",
        "noscript",
    ]

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

    def parse_page(self, url: str) -> Dict[str, Any]:
        """Fetch and parse a web page."""
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return {
            "url": url,
            "domain": urlparse(url).netloc,
            "status_code": resp.status_code,
            "metadata": self.extract_metadata(soup),
            "main_text": self.extract_main_content(soup),
            "all_text": self.extract_all_text(soup),
            "structure": self.analyze_structure(soup),
        }

    @staticmethod
    def extract_metadata(soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract title/description/keywords/lang/charset when available."""
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        meta_desc = ""
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        if meta_desc_tag:
            meta_desc = (meta_desc_tag.get("content") or "").strip()
        keywords = ""
        kw_tag = soup.find("meta", attrs={"name": "keywords"})
        if kw_tag:
            keywords = (kw_tag.get("content") or "").strip()
        author = ""
        author_tag = soup.find("meta", attrs={"name": "author"})
        if author_tag:
            author = (author_tag.get("content") or "").strip()
        lang = (soup.html.get("lang") if soup.html else "") or ""
        charset = ""
        charset_tag = soup.find("meta", attrs={"charset": True})
        if charset_tag:
            charset = (charset_tag.get("charset") or "").strip()
        return {
            "title": title,
            "description": meta_desc,
            "keywords": keywords,
            "author": author,
            "lang": lang,
            "charset": charset,
        }

    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text using simple heuristics."""
        soup = BeautifulSoup(str(soup), "html.parser")
        for tag_name in self.EXCLUDE_SELECTORS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        candidates: List[str] = []
        for sel in self.CONTENT_SELECTORS:
            found = soup.select(sel)
            if not found:
                continue
            # pick the largest by text length
            best = max(found, key=lambda el: len(el.get_text(" ", strip=True)))
            candidates.append(best.get_text(" ", strip=True))
        if candidates:
            return max(candidates, key=len)
        body = soup.body
        return (
            body.get_text(" ", strip=True) if body else soup.get_text(" ", strip=True)
        )

    @staticmethod
    def extract_all_text(soup: BeautifulSoup) -> str:
        """Extract all visible text (best-effort)."""
        soup = BeautifulSoup(str(soup), "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)

    @staticmethod
    def analyze_structure(soup: BeautifulSoup) -> Dict[str, Any]:
        """Count structural elements (headings, lists, tables, forms, media)."""
        return {
            "headings": {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)},
            "paragraphs": len(soup.find_all("p")),
            "lists": len(soup.find_all(["ul", "ol"])),
            "forms": len(soup.find_all("form")),
            "tables": len(soup.find_all("table")),
            "images": len(soup.find_all("img")),
            "videos": len(soup.find_all(["video", "iframe"])),
            "external_links": len(
                [
                    a
                    for a in soup.find_all("a", href=True)
                    if a["href"].startswith("http")
                ]
            ),
        }

    def extract_text_by_selector(self, url: str, selector: str) -> Dict[str, Any]:
        """Fetch a page and extract text from elements matching a CSS selector."""
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        elements = soup.select(selector)
        texts = [
            el.get_text(" ", strip=True) for el in elements if el.get_text(strip=True)
        ]
        return {"url": url, "selector": selector, "matches": len(texts), "texts": texts}

    def compare_pages(self, url1: str, url2: str) -> Dict[str, Any]:
        """Compare two pages by simple Jaccard similarity of word sets."""
        try:
            p1 = self.parse_page(url1)
            p2 = self.parse_page(url2)
        except Exception:
            return {"error": "Failed to load one or both pages"}
        t1 = p1.get("main_text", "") or ""
        t2 = p2.get("main_text", "") or ""
        similarity = self._jaccard_similarity(t1, t2)
        return {
            "url1": url1,
            "url2": url2,
            "similarity_pct": similarity,
            "len1": len(t1),
            "len2": len(t2),
        }

    @staticmethod
    def _jaccard_similarity(text1: str, text2: str) -> float:

        def norm_words(t: str) -> set[str]:
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", t.lower())
            return set(words)

        s1 = norm_words(text1)
        s2 = norm_words(text2)
        if not s1 and not s2:
            return 100.0
        inter = len(s1.intersection(s2))
        union = len(s1.union(s2)) or 1
        return round((inter / union) * 100, 2)
