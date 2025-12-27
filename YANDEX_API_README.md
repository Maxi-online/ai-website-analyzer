# Yandex API Integration

This document describes how to configure and use Yandex APIs in the **SEO microservice** of this project.

## Overview

The project supports both **legacy** and **modern** Yandex integrations:

- **Yandex Suggest API** (public) — query suggestions
- **Yandex Wordstat API** — keyword statistics (requires token)
- **Yandex Cloud API** — optional data enrichment (requires key)
- **Yandex Direct API** — optional advertising data (requires OAuth/client credentials)
- **Legacy Wordstat v4** — kept for backward compatibility

## Configuration

All secrets must be provided via environment variables. Never commit real keys to git.

### Modern Yandex keys

```env
# Modern Yandex API credentials (EXAMPLE VALUES)
YANDEX_WORDSTAT_TOKEN=y0__example_token
YANDEX_CLOUD_API_KEY=example_yandex_cloud_api_key
YANDEX_CLIENT_ID=example_yandex_client_id
YANDEX_CLIENT_SECRET=example_yandex_client_secret

# Yandex API URLs (defaults are OK for most users)
YANDEX_SUGGEST_URL=https://suggest.yandex.ru/suggest-ya.cgi
YANDEX_DIRECT_URL=https://api.direct.yandex.ru/v4/json/
YANDEX_CLOUD_URL=https://cloud-api.yandex.net/v1/
```

### Legacy credentials (optional)

```env
# Legacy Yandex Wordstat v4 (optional)
YANDEX_URL=https://api-sandbox.direct.yandex.ru/v4/json/
YANDEX_TOKEN=example_legacy_token
YANDEX_USERNAME=example_legacy_username
```

## How it is used in this repo

- The **SEO service** exposes an endpoint `POST /modern_keywords` which may use modern Yandex APIs.
- The legacy Wordstat flow is exposed as `POST /wordstat`.

## Example: calling the SEO microservice

### Get modern keyword ideas

```bash
curl -X POST http://localhost:8001/modern_keywords ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"best restaurants in moscow\",\"knowledge_base\":{\"restaurant_name\":\"Example Restaurant\",\"cuisine_type\":\"Mediterranean\"}}"
```

### Get Wordstat keyword statistics (legacy)

```bash
curl -X POST http://localhost:8001/wordstat ^
  -H "Content-Type: application/json" ^
  -d "{\"keywords\":[\"best restaurants in moscow\",\"restaurants near me\"]}"
```

## Notes

- If you do not configure Yandex credentials, the SEO service should still run, but will skip Yandex-dependent features.
- Make sure you configure the correct region/locale in the code if your project requires specific Wordstat regions.

