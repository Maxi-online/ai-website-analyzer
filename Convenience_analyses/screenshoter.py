# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

Screenshots helper for design analysis.

This module can capture screenshots via the Bright Data MCP server and prepare

them in a format compatible with image inputs for OpenAI models.

"""

import asyncio
import base64
import logging
from typing import Any, Dict, List, Optional

from .mcp_client import BrightDataMCPClient, BrightDataMCPError

logger = logging.getLogger(__name__)


class ScreenshotAnalyzer:
    """
    Capture screenshots and prepare them for design analysis.
    """

    def __init__(self, mcp_client: Optional[BrightDataMCPClient] = None):
        """
        Initialize the screenshots analyzer.
        """
        self.mcp_client = mcp_client
        if not self.mcp_client:
            try:
                self.mcp_client = BrightDataMCPClient()
            except BrightDataMCPError as e:
                logger.warning("Failed to initialize MCP client: %s", e)
                self.mcp_client = None

    async def capture_screenshots(self, url: str) -> Dict[str, Any]:
        """
        Capture screenshots for multiple viewports.
        """
        result = {"status": "error", "screenshots": {}, "message": ""}
        if not self.mcp_client:
            result["message"] = "MCP client is not available for screenshots"
            return result
        try:
            # Capture different viewports in parallel
            tasks = {
                "desktop": self.mcp_client.capture_screenshot(url, viewport="desktop"),
                "mobile": self.mcp_client.capture_screenshot(url, viewport="mobile"),
            }
            screenshots = {}
            for device, task in tasks.items():
                try:
                    response = await task
                    # Bright Data MCP returns base64 screenshot payload
                    if response and "screenshot" in response:
                        screenshots[device] = {
                            "base64": response["screenshot"],
                            "format": response.get("format", "png"),
                            "width": response.get("width"),
                            "height": response.get("height"),
                            "url": url,
                        }
                        logger.info("Screenshot %s created for %s", device, url)
                    else:
                        logger.warning(
                            "Failed to get screenshot %s for %s", device, url
                        )
                except Exception as e:
                    logger.error("Error while creating screenshot %s: %s", device, e)
            if screenshots:
                result["status"] = "success"
                result["screenshots"] = screenshots
                result["message"] = f"Screenshots created: {len(screenshots)}"
            else:
                result["message"] = "No screenshots were created"
        except Exception as e:
            result["message"] = f"Error while creating screenshots: {str(e)}"
            logger.error("Error in capture_screenshots: %s", e)
        return result

    def prepare_for_gpt5_vision(
        self, screenshots: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Prepare screenshot payloads for image inputs.
        """
        images = []
        for device, screenshot_data in screenshots.items():
            if screenshot_data and "base64" in screenshot_data:
                # Format for image inputs
                image_data = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{screenshot_data.get('format', 'png')};base64,{screenshot_data['base64']}",
                        "detail": "high",
                    },
                }
                # Optional metadata
                if screenshot_data.get("width") and screenshot_data.get("height"):
                    image_data["metadata"] = {
                        "device": device,
                        "width": screenshot_data["width"],
                        "height": screenshot_data["height"],
                    }
                images.append(image_data)
                logger.info("Prepared %s screenshot for image input", device)
        return images

    async def analyze_design(self, url: str) -> Dict[str, Any]:
        """
        Capture screenshots and prepare them for design analysis.
        """
        result = {
            "status": "error",
            "url": url,
            "screenshots_created": False,
            "vision_data": [],
            "design_aspects": {},
            "message": "",
        }
        try:
            # Capture screenshots
            screenshot_result = await self.capture_screenshots(url)
            if screenshot_result["status"] == "success":
                result["screenshots_created"] = True
                # Prepare images payload
                vision_data = self.prepare_for_gpt5_vision(
                    screenshot_result["screenshots"]
                )
                result["vision_data"] = vision_data
                # Prompts/hints for design analysis
                result["design_aspects"] = {
                    "visual_hierarchy": "Evaluate visual hierarchy and layout of key elements",
                    "color_scheme": "Evaluate color scheme and brand consistency",
                    "typography": "Evaluate typography, readability, and font usage",
                    "spacing": "Check spacing, alignment, and whitespace usage",
                    "consistency": "Evaluate consistency across UI components",
                    "modern_trends": "Alignment with modern web design conventions",
                    "mobile_adaptation": "Mobile responsiveness and UX quality",
                    "visual_appeal": "Overall visual appeal and professionalism",
                    "user_focus": "Support for user tasks and CTA clarity",
                    "accessibility": "Visual accessibility (contrast, tap targets, font sizes)",
                }
                result["status"] = "success"
                result["message"] = "Screenshots captured and prepared for analysis"
            else:
                result["message"] = screenshot_result.get(
                    "message", "Failed to create screenshots"
                )
        except Exception as e:
            result["message"] = f"Error while preparing design analysis: {str(e)}"
            logger.error("Error in analyze_design: %s", e)
        return result


async def create_design_analysis_data(url: str) -> Dict[str, Any]:
    """
    Helper to create design analysis payload for a URL.
    """
    analyzer = ScreenshotAnalyzer()
    return await analyzer.analyze_design(url)
