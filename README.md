# Analytics Microservices Platform

Comprehensive website analytics platform built on a microservices architecture and GPT-5.

## Architecture

The project consists of **5 independent components**:

```
analytics/
├── SEO_analyses/          # SEO Analysis Microservice
├── Text_analyses/         # Text Analysis Microservice
├── Convenience_analyses/  # UX/UI & Performance Microservice
├── Senior_analyser/       # Aggregation & Comparison Microservice
└── Desktop_app/           # GUI Application
```

## Microservices

### 1. SEO_analyses (Port: 8001)
**Purpose:** SEO analysis for websites
- Meta tags, headings, URL structure analysis
- Optional integration with Yandex Wordstat (legacy Direct API)
- GPT-5 for synthesized recommendations

**Tech:** FastAPI, BeautifulSoup, OpenAI GPT-5

### 2. Text_analyses (Port: 8002)
**Purpose:** Text/content analysis
- Readability and structure signals
- Content statistics
- GPT-5 for quality assessment

**Tech:** FastAPI, TextStat, OpenAI GPT-5

### 3. Convenience_analyses (Port: 8003)
**Purpose:** UX/UI and usability analysis
- Optional screenshots via ScreenshotOne (if configured)
- Basic accessibility and responsive heuristics (best-effort)
- GPT-5 for UX report generation

**Tech:** FastAPI, BeautifulSoup, ScreenshotOne (optional), OpenAI GPT-5

### 4. Senior_analyser (Port: 8004)
**Purpose:** Aggregation and comparison
- Collects results from all microservices
- Compares two websites
- Produces a final report
- GPT-5 for expert-level synthesis

**Tech:** FastAPI, aiohttp/httpx, OpenAI GPT-5

### 5. Desktop_app
**Purpose:** End-user GUI
- Enter site URLs
- Start analysis via `Senior_analyser`
- View results

**Tech:** Python, tkinter, requests

## Quick start

### Requirements
- Docker & Docker Compose
- OpenAI API key (for GPT-5)

### 1) Environment variables

Copy `env.example` to `.env` and fill in the required values:
```bash
cp env.example .env
```

Required variables:
```env
OPENAI_API_KEY=sk-example-your-openai-key
```

### 2) Run via Docker

```bash
# Rebuild and start all containers
docker-compose up --build -d

# Status
docker-compose ps

# Logs
docker-compose logs -f
```

### 3) Stop services

```bash
docker-compose down
```

## API testing

### SEO Analysis
```bash
curl -X POST http://localhost:8001/seo_analysis \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Text Analysis
```bash
curl -X POST http://localhost:8002/text_analysis \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Convenience Analysis
```bash
curl -X POST http://localhost:8003/convenience_analysis \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Senior Comparison
```bash
curl -X POST http://localhost:8004/compare_sites \
  -H "Content-Type: application/json" \
  -d '{"site1_url": "https://site1.com", "site2_url": "https://site2.com"}'
```

## Development

### Microservice layout
Each microservice is self-contained:
```
SEO_analyses/
├── settings.py           # Service-local settings
├── requirements.txt      # Service dependencies
├── Dockerfile            # Docker image definition
├── main.py               # FastAPI application
├── gpt5_agent.py         # GPT-5 integration
└── [specific modules]    # Service-specific logic
```

### Adding a new microservice
1. Create a folder for the service
2. Add `settings.py`, `requirements.txt`, `Dockerfile`
3. Implement the FastAPI app in `main.py`
4. Add the service to `docker-compose.yml`

## Documentation

- **Yandex API**: `YANDEX_API_README.md`

## Configuration

### OpenAI GPT-5
```env
OPENAI_MODEL=gpt-5-nano
OPENAI_VERBOSITY=medium
OPENAI_REASONING_EFFORT=medium
```

### Proxy
```env
PROXY_ENABLED=false
PROXY_HOST=your_proxy_host
PROXY_PORT=your_proxy_port
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
```

### Bright Data MCP
```env
BRIGHTDATA_API_TOKEN=your_token_here
```

## Architectural decisions

### Microservices
- Independent services
- Separate `settings.py` and `requirements.txt`
- HTTP-based communication
- Docker-based horizontal scaling

### GPT-5 Integration
- Responses API (instead of legacy Chat Completions)
- Async calls via `httpx`
- Proxy support for outbound requests

### Temporary files
- Ignored via `.gitignore`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m "Add AmazingFeature"`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Author

Maxim Strekolovskiy

## License

MIT License - see [LICENSE](LICENSE)

## 👥 Authors

Maxim Strekolovskiy

## 🙏 Acknowledgments

- OpenAI GPT-5 for intelligent analysis
- Bright Data MCP for screenshots/web automation (optional)
- Yandex APIs for SEO-related data (optional)