# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""

FastAPI application for the `Senior_analyser` (aggregator) microservice.

This service orchestrates other microservices (SEO/Text/Convenience) and can:

- compare two websites

- analyze a single website

- generate recommendations vs a competitor

"""

import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .senior_analyser import SeniorAnalyzer
from .settings import settings

# Initialize analyzer

senior_analyzer = SeniorAnalyzer()

app = FastAPI(
    title="Senior Analyser Service",
    description=(
        "Aggregator service for website comparison and recommendation generation "
        "using microservices and GPT-5."
    ),
    version="1.0.0",
)


@app.get("/")
async def root():
    """
    Service metadata.
    """
    return {
        "service": "Senior Analyser Service",
        "version": "1.0.0",
        "endpoints": {
            "/compare_sites": "Compare two websites (plain text report)",
            "/generate_recommendations": "Generate recommendations vs a competitor",
            "/analyze_single_site": "Analyze a single website",
            "/service_status": "Check status of dependent microservices",
        },
        "features": [
            "Website comparison across categories",
            "Recommendations and action plan",
            "Single-site analysis mode",
            "Microservice orchestration (SEO/Text/Convenience)",
            "GPT-5 based reporting",
            "Microservice status monitoring",
        ],
    }


class CompareSitesRequest(BaseModel):
    """Request payload for comparing two websites."""

    site1_url: str
    site2_url: str


class GenerateRecommendationsRequest(BaseModel):
    """Request payload for generating recommendations."""

    site_url: str
    competitor_url: str


class AnalyzeSingleSiteRequest(BaseModel):
    """Request payload for analyzing a single website."""

    url: str


@app.post("/compare_sites", response_class=PlainTextResponse)
async def compare_sites_endpoint(request: CompareSitesRequest):
    """
    Compare two websites and return a plain-text report.
    """
    try:
        result = await senior_analyzer.compare_sites(
            request.site1_url, request.site2_url
        )
        return PlainTextResponse(content=result, media_type="text/plain; charset=utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/generate_recommendations")
async def generate_recommendations_endpoint(request: GenerateRecommendationsRequest):
    """
    Generate recommendations for improving a website by comparing it to a competitor.
    """
    try:
        result = await senior_analyzer.generate_recommendations(
            request.site_url, request.competitor_url
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/analyze_single_site")
async def analyze_single_site_endpoint(request: AnalyzeSingleSiteRequest):
    """
    Analyze a single website and return structured data plus recommendations.
    """
    try:
        result = await senior_analyzer.analyze_single_site(request.url)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/service_status")
async def service_status_endpoint():
    """
    Check status of all dependent microservices in the system.
    """
    try:
        result = await senior_analyzer.get_service_status()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
async def health_check():
    """
    Liveness/health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Senior Analyser Service",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "Senior_analyser.main:app",
        host="0.0.0.0",
        port=settings.SENIOR_SERVICE_PORT,
        reload=True,
    )
