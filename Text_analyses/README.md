# Text Analyses Service

Microservice for analyzing web page text content and returning a plain-text report.

## Features

- Basic text extraction and structure signals (headings, paragraphs, lists, images with alt)
- Readability metrics (English-oriented)
- Keyword frequency and density (stop-word filtered)
- Simple repetition and uniqueness indicators
- GPT-5 synthesis into a human-readable report

## Configuration

Use environment variables (see root `env.example`).

Required:

```env
OPENAI_API_KEY=sk-example-your-openai-key
OPENAI_MODEL=gpt-5-nano
```

## Run

```bash
pip install -r Text_analyses/requirements.txt
python -m uvicorn Text_analyses.main:app --host 0.0.0.0 --port 8002
```

## API

### POST `/text_analysis`

Request:

```json
{"url":"https://example.com"}
```

Response:

- `text/plain` — analysis report (English)

