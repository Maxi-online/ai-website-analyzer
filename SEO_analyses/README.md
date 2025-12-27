# SEO Analyses Service

Comprehensive microservice for SEO analysis of websites.

## Features

- **Meta tags analysis**: title, description, keywords, Open Graph
- **Core Web Vitals**: LCP, FID, CLS (optional)
- **Heading structure**: H1-H6 analysis and hierarchy checks
- **URL structure**: readability and SEO-friendliness heuristics
- **Links analysis**: internal and external links
- **Mobile friendliness**: viewport and responsive design checks
- **Yandex Wordstat**: keyword statistics (legacy API)
- **Overall SEO score**: composite score from 0 to 100

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file (not committed) or export environment variables:

```env
YANDEX_URL=https://api-sandbox.direct.yandex.ru/v4/json/
YANDEX_TOKEN=your_token
YANDEX_USERNAME=your_login

SEO_SERVICE_PORT=8001
```

## Run

```bash
python -m SEO_analyses.main
```

The service will be available at `http://localhost:8001`.

## API Endpoints

### GET /

Service metadata and available endpoints.

### POST /seo_analysis

Full SEO analysis for a page (plain text report).

**Request:**

```json
{
    "url": "https://example.com"
}
```

**Response:**

```json
{
    "url": "https://example.com",
    "status_code": 200,
    "seo_score": 85,
    "meta_tags": {
        "title": {
            "content": "Example Title",
            "length": 13,
            "status": "good"
        },
        "description": {
            "content": "Example description",
            "length": 19,
            "status": "good"
        }
    },
    "headings": {
        "h1": {"count": 1, "content": ["Main Title"]},
        "h2": {"count": 3, "content": ["Section 1", "Section 2"]},
        "structure_score": 50
    },
    "core_web_vitals": {
        "lcp": {"value": 2.1, "status": "good"},
        "fid": {"value": 50, "status": "good"},
        "cls": {"value": 0.05, "status": "good"},
        "score": 100
    },
    "mobile_friendly": {
        "viewport_meta": true,
        "responsive_design": true,
        "score": 100
    }
}
```

### POST /wordstat

Keyword statistics via Yandex Wordstat (legacy API).

**Request:**

```json
{
    "keywords": ["seo", "analysis", "optimization"]
}
```

### POST /parse_head

Parse the page <head> section.

**Request:**

```json
{
    "url": "https://example.com"
}
```

## Project structure

```text
SEO_analyses/
├── __init__.py
├── main.py              # FastAPI application
├── seo_analyser.py      # Main SEO analyzer
├── head_parser.py       # <head> parser
├── wsparser.py          # Yandex Wordstat parser
└── README.md            # Documentation
```

## SEO score breakdown

The SEO score is computed using the following criteria:

- **Meta tags (30 points)**: title, description, Open Graph
- **Headings (20 points)**: H1-H6 structure
- **URL structure (15 points)**: readability and consistency
- **Links (15 points)**: internal and external links
- **Core Web Vitals (15 points)**: performance
- **Mobile friendliness (5 points)**: responsive design

## Requirements

- Python 3.8+
- FastAPI
- BeautifulSoup4
- Requests
- Selenium (for dynamic content)
- Google PageSpeed Insights API key (optional)
- Yandex Wordstat API access
