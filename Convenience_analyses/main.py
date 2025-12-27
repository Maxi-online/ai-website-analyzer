# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

"""FastAPI entrypoint for the Convenience (UX) microservice."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .convenience_analyser import ConvenienceAnalyzer
from .settings import settings

convenience_analyzer = ConvenienceAnalyzer()

app = FastAPI(
    title="Convenience Analyses Service",
    description=(
        "UX and accessibility analysis for websites. This service can optionally use screenshots "
        "to assess visual design and usability."
    ),
    version="2.0.0",
)


@app.get("/")
async def root():
    """
    Service info.
    """
    return {
        "service": "Convenience Analyses Service",
        "version": "2.0.0",
        "endpoints": {
            "/convenience_analysis": "Full UX/usability analysis (plain text report)",
        },
        "features": [
            "Navigation usability checks",
            "Responsive design heuristics",
            "Accessibility heuristics",
            "Optional visual design analysis via screenshots",
            "GPT-5 agent synthesis",
            "Overall UX score",
        ],
        "note": "Performance and Core Web Vitals are handled by the SEO service.",
    }


class ConvenienceAnalysisRequest(BaseModel):
    url: str


@app.post("/convenience_analysis", response_class=PlainTextResponse)
async def convenience_analysis_endpoint(request: ConvenienceAnalysisRequest):
    """
    Run a full UX analysis for a given URL.
    Returns a plain text report.
    """
    try:
        result = await convenience_analyzer.analyze_url(request.url)
        return PlainTextResponse(content=result, media_type="text/plain; charset=utf-8")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "Convenience_analyses.main:app",
        host="0.0.0.0",
        port=settings.CONVENIENCE_SERVICE_PORT,
        reload=True,
    )
