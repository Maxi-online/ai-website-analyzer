# SPDX-License-Identifier: MIT

# Copyright (c) 2025 Maxim Strekolovskiy

# SEO_analyses/head_parser.py

import urllib.request

from bs4 import BeautifulSoup


def parse_head(html_content: str) -> str:
    """
    Extract the <head> HTML from a full HTML document string.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    head_tag = soup.find("head")
    return head_tag.prettify() if head_tag else ""


def fetch_and_parse_head(url: str) -> str:
    """
    Fetch a URL and return the extracted <head> HTML.
    """
    with urllib.request.urlopen(url) as response:
        html_content = response.read()
    return parse_head(html_content)
