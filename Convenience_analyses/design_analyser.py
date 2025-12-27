# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Maxim Strekolovskiy

"""
Design analyzer (optional helper).

This module is intentionally self-contained and safe for OSS publication.
It does not require secrets and does not make network calls.

If you later decide to use screenshot-based visual heuristics in the UX service,
this module is the place to implement them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DesignAnalysisResult:
    """Lightweight container for optional visual/design heuristics."""

    score: int
    notes: str
    details: Dict[str, Any]


class DesignAnalyzer:
    """
    Optional visual design analyzer.
    Current implementation is conservative by design: it returns a placeholder
    result so the module is not empty/truncated and can be safely extended.
    """

    def analyze(
        self,
        *,
        html: Optional[str] = None,
        screenshot_metadata: Optional[Dict[str, Any]] = None,
    ) -> DesignAnalysisResult:
        """
        Analyze visual design heuristics (placeholder).
        Args:
            html: Optional HTML source (if you want to derive style signals).
            screenshot_metadata: Optional metadata about screenshots/viewports.
        """
        details: Dict[str, Any] = {
            "has_html": bool(html),
            "has_screenshot_metadata": bool(screenshot_metadata),
        }
        return DesignAnalysisResult(
            score=0,
            notes="Design analysis is not enabled in this OSS build.",
            details=details,
        )
