# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""FastAPI entrypoint for the Text Analyses microservice."""

import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .settings import settings
from .text_analyser import TextAnalyzer
from .webpage_parser import WebPageParser

text_analyzer = TextAnalyzer()

webpage_parser = WebPageParser()

app = FastAPI(
    title="Text Analyses Service",
    description="Text/content analysis for web pages (readability, structure, signals).",
    version="1.0.0",
)


@app.get("/")
async def root():
    """Service info."""
    return {
        "service": "Text Analyses Service",
        "version": "1.0.0",
        "endpoints": {
            "/text_analysis": "Full text analysis (plain text report)",
            "/parse_page": "Parse a page and extract structured content",
            "/extract_by_selector": "Extract text by CSS selector",
            "/compare_pages": "Compare content of two pages",
        },
    }


class TextAnalysisRequest(BaseModel):
    url: str


class ParsePageRequest(BaseModel):
    url: str


class ExtractBySelectorRequest(BaseModel):
    url: str
    selector: str


class ComparePagesRequest(BaseModel):
    url1: str
    url2: str


@app.post("/text_analysis", response_class=PlainTextResponse)
async def text_analysis_endpoint(request: TextAnalysisRequest):
    """Run text analysis for a URL and return a plain-text report."""
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None, text_analyzer.analyze_url, request.url
        )
        return PlainTextResponse(content=result, media_type="text/plain; charset=utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/parse_page")
async def parse_page_endpoint(request: ParsePageRequest):
    """Parse a web page and return extracted content and metadata."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, webpage_parser.parse_page, request.url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/extract_by_selector")
async def extract_by_selector_endpoint(request: ExtractBySelectorRequest):
    """Extract text by CSS selector."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(
            None, webpage_parser.extract_text_by_selector, request.url, request.selector
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/compare_pages")
async def compare_pages_endpoint(request: ComparePagesRequest):
    """Compare the text content of two pages."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(
            None, webpage_parser.compare_pages, request.url1, request.url2
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health_check():
    """Health check."""
    return {"status": "healthy", "service": "Text Analyses Service", "version": "1.0.0"}


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "Text_analyses.main:app",
        host="0.0.0.0",
        port=settings.TEXT_SERVICE_PORT,
        reload=True,
    )
