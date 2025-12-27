# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Text analyzer for the Text Analyses microservice.

This module collects deterministic text/content signals from a web page and then

uses the GPT-5 agent to generate a plain-text report.

"""

from __future__ import annotations

import asyncio
import re
from collections import Counter
from typing import Any, Dict, List
from urllib.parse import urlparse

import textstat

from .gpt5_agent import TextAnalysisAgent
from .webpage_parser import WebPageParser


class TextAnalyzer:
    """Compute text signals for a URL and ask GPT-5 to produce a report."""

    DEFAULT_STOP_WORDS: set[str] = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "he",
        "her",
        "his",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "me",
        "my",
        "no",
        "not",
        "of",
        "on",
        "or",
        "our",
        "she",
        "so",
        "that",
        "the",
        "their",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "to",
        "too",
        "us",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "will",
        "with",
        "you",
        "your",
    }

    def __init__(self) -> None:
        self.parser = WebPageParser()
        self.agent = TextAnalysisAgent()

    def analyze_url(self, url: str) -> str:
        """
        Build a payload of text/content signals and return a plain-text GPT report.
        """
        page = self.parser.parse_page(url)
        main_text = (page.get("main_text") or "").strip()
        if not main_text:
            return f"Text analysis failed: no extractable main content for {url}"
        tokens = self._tokenize_words(main_text)
        payload: Dict[str, Any] = {
            "url": url,
            "domain": urlparse(url).netloc,
            "status_code": page.get("status_code"),
            "metadata": page.get("metadata", {}),
            "structure": page.get("structure", {}),
            "text_content": {
                "length_chars": len(main_text),
                "word_count": len(tokens),
                "preview": main_text[:500] + ("..." if len(main_text) > 500 else ""),
            },
            "readability": self._readability(main_text),
            "keywords": self._keywords(tokens),
            "stopword_share": self._stopword_share(tokens),
            "repetition": self._repetition(tokens),
            "uniqueness": self._uniqueness(main_text, tokens),
        }
        result = asyncio.run(self.agent.analyze(payload))
        return result.get("analysis", str(result))

    @staticmethod
    def _tokenize_words(text: str) -> List[str]:
        words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())
        return [w for w in words if len(w) >= 2]

    @staticmethod
    def _readability(text: str) -> Dict[str, Any]:
        try:
            return {
                "flesch_reading_ease": float(textstat.flesch_reading_ease(text)),
                "flesch_kincaid_grade": float(textstat.flesch_kincaid_grade(text)),
                "gunning_fog": float(textstat.gunning_fog(text)),
                "smog_index": float(textstat.smog_index(text)),
                "dale_chall": float(textstat.dale_chall_readability_score(text)),
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _keywords(self, tokens: List[str]) -> Dict[str, Any]:
        filtered = [t for t in tokens if t not in self.DEFAULT_STOP_WORDS]
        freq = Counter(filtered)
        total = len(filtered) or 1
        top: list[dict[str, Any]] = []
        for word, count in freq.most_common(20):
            top.append(
                {
                    "keyword": word,
                    "count": count,
                    "density_pct": round((count / total) * 100, 2),
                }
            )
        return {"total_words": len(filtered), "unique_words": len(freq), "top": top}

    def _stopword_share(self, tokens: List[str]) -> Dict[str, Any]:
        if not tokens:
            return {"stopword_share_pct": 0.0}
        stop = sum(1 for t in tokens if t in self.DEFAULT_STOP_WORDS)
        return {"stopword_share_pct": round((stop / len(tokens)) * 100, 2)}

    @staticmethod
    def _repetition(tokens: List[str]) -> Dict[str, Any]:
        if not tokens:
            return {"max_word_share_pct": 0.0}
        freq = Counter(tokens)
        top_word, top_count = freq.most_common(1)[0]
        return {
            "most_common_word": top_word,
            "most_common_count": top_count,
            "max_word_share_pct": round((top_count / len(tokens)) * 100, 2),
        }

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p.strip() for p in parts if p.strip()]

    def _uniqueness(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        sentences = self._split_sentences(text)
        unique_words = len(set(tokens))
        lexical_diversity = round((unique_words / (len(tokens) or 1)) * 100, 2)
        repeated_sentences = 0
        seen: set[str] = set()
        for s in sentences:
            key = s.lower()
            if key in seen:
                repeated_sentences += 1
            else:
                seen.add(key)
        return {
            "sentence_count": len(sentences),
            "lexical_diversity_pct": lexical_diversity,
            "repeated_sentences": repeated_sentences,
        }
