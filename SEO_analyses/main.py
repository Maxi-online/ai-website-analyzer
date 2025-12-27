# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

# SEO_analyses/main.py

import asyncio
import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .head_parser import fetch_and_parse_head
from .wsparser import WordstatParser

# Wordstat access configuration

YANDEX_URL = os.getenv("YANDEX_URL", "https://api-sandbox.direct.yandex.ru/v4/json/")

YANDEX_TOKEN = os.getenv("YANDEX_TOKEN", "")

YANDEX_USERNAME = os.getenv("YANDEX_USERNAME", "")

# Initialize Wordstat parser

parser = WordstatParser(YANDEX_URL, YANDEX_TOKEN, YANDEX_USERNAME)

app = FastAPI(title="SEO Analyses Service")

# Request model for Wordstat


class WordstatRequest(BaseModel):
    keywords: List[str]


# Request model for <head> parsing


class HeadRequest(BaseModel):
    url: str


@app.post("/wordstat")
async def get_wordstat(request: WordstatRequest):
    """
    Accepts a list of keywords, requests Wordstat statistics (region Moscow = 213),
    and returns phrases with their frequency.
    """
    loop = asyncio.get_running_loop()

    def process_wordstat(keywords: list[str]) -> dict:
        # Step 1: Create a report for the provided keywords and region Moscow (ID = 213)
        response = parser.createReport(keywords, [213])
        if "data" not in response:
            raise Exception("Failed to create report: " + str(response))
        report_id = response["data"]
        # Step 2: Wait for the report to be ready (max 30 iterations)
        attempts = 0
        while True:
            report_list = parser.getReportList()
            if "data" not in report_list or not report_list["data"]:
                raise Exception("Failed to get report list: " + str(report_list))
            # Assume the newly created report is the last item in the list
            last_report = report_list["data"][-1]
            status = last_report.get("StatusReport")
            if status == "Done":
                break
            elif status == "Failed":
                raise Exception("Report generation failed (Failed).")
            time.sleep(2)
            attempts += 1
            if attempts > 30:
                raise Exception("Timed out waiting for report generation.")
        # Step 3: Read the report
        report_data = parser.readReport(report_id)
        if "data" not in report_data:
            raise Exception("Failed to read report: " + str(report_data))
        # Step 4: Build the result list (SearchedWith column)
        result_keywords = []
        for entry in report_data["data"]:
            for item in entry.get("SearchedWith", []):
                phrase = item.get("Phrase")
                shows = item.get("Shows")
                result_keywords.append({"phrase": phrase, "shows": shows})
        # Step 5: Delete the report (Direct API limits stored reports)
        parser.deleteReport(report_id)
        return {"keywords": result_keywords}

    try:
        result = await loop.run_in_executor(None, process_wordstat, request.keywords)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/parse_head")
def parse_head_endpoint(request: HeadRequest):
    """
    Accepts a URL, loads the page, and returns the contents of the <head> tag.
    """
    try:
        head_content = fetch_and_parse_head(request.url)
        return {"head": head_content}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":

    import uvicorn

    uvicorn.run("SEO_analyses.main:app", host="0.0.0.0", port=8001, reload=True)
