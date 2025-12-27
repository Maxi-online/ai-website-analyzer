# Convenience (UX) Analyses Service

Microservice for **UX/usability and basic accessibility** analysis of websites.

## Features

- **Navigation heuristics**: menus, breadcrumbs, search presence, internal/external link counts
- **Accessibility heuristics**: alt coverage, ARIA/semantic elements, headings and form label signals
- **Responsive heuristics**: viewport meta, media queries, basic layout signals
- **Optional screenshots**: can capture screenshots via ScreenshotOne (if configured)
- **GPT-5 synthesis**: produces a plain-text UX report with scores and an action plan

## Configuration

Use environment variables (see root `env.example`).

Required:

```env
OPENAI_API_KEY=sk-example-your-openai-key
OPENAI_MODEL=gpt-5-nano
```

Optional (screenshots):

```env
SCREENSHOTONE_ACCESS_KEY=example_access_key
SCREENSHOTONE_SECRET_KEY=example_secret_key
SCREENSHOTONE_API_URL=https://api.screenshotone.com/take
```

## Run

```bash
pip install -r Convenience_analyses/requirements.txt
python -m uvicorn Convenience_analyses.main:app --host 0.0.0.0 --port 8003
```

## API

### POST `/convenience_analysis`

Request:

```json
{"url":"https://example.com"}
```

Response:

- `text/plain` — UX report in plain text (English)

