# Senior Analyser Service

Aggregator microservice for website comparison and recommendation generation using GPT-5 agents.

## Features

- **Website comparison** — compare two websites across all categories
- **Recommendations** — generate a prioritized improvement plan
- **Single-site analysis** — analyze one website with recommendations
- **Microservice orchestration** — coordinates SEO, Text, and Convenience services
- **GPT-5 agents** — reasoning-based analysis and report generation
- **Service monitoring** — health/status checks for all microservices
- **Competitive analysis** — high-level competitive advantages review

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables (see `env.example` at the repo root):

```env
OPENAI_API_KEY=sk-your_key_here
OPENAI_MODEL=gpt-5-nano

SEO_SERVICE_PORT=8001
TEXT_SERVICE_PORT=8002
CONVENIENCE_SERVICE_PORT=8003
SENIOR_SERVICE_PORT=8004
```

## Run

```bash
python -m Senior_analyser.main
```

The service will be available at `http://localhost:8004`.

## API Endpoints

### POST /compare_sites

Compare two websites.

**Request:**
```json
{
    "site1_url": "https://mysite.com",
    "site2_url": "https://competitor.com"
}
```

**Response:**
```json
{
    "site1_url": "https://mysite.com",
    "site2_url": "https://competitor.com",
    "raw_data": {
        "site1": {
            "seo_analysis": {...},
            "text_analysis": {...},
            "convenience_analysis": {...}
        },
        "site2": {
            "seo_analysis": {...},
            "text_analysis": {...},
            "convenience_analysis": {...}
        }
    },
    "gpt5_analysis": {
        "agent_type": "senior_analysis",
        "status": "success",
        "analysis": {
            "comparison_summary": "Short comparison summary",
            "winner_by_category": {
                "seo": "site1",
                "text_quality": "site2",
                "convenience": "site1",
                "overall": "site1"
            },
            "improvement_recommendations": [
                {
                    "category": "SEO",
                    "priority": "high",
                    "recommendation": "Improve meta tags",
                    "expected_impact": "Increase traffic by 20%"
                }
            ],
            "competitive_analysis": "Competitive advantages analysis",
            "action_plan": ["Prioritized action plan"],
            "overall_score": {
                "site1": 75,
                "site2": 68
            }
        }
    },
    "comparison_summary": "Short comparison summary",
    "overall_scores": {
        "site1": 75,
        "site2": 68
    }
}
```

### POST /generate_recommendations

Generate recommendations to improve a website.

**Request:**
```json
{
    "site_url": "https://mysite.com",
    "competitor_url": "https://competitor.com"
}
```

**Response:**
```json
{
    "site_url": "https://mysite.com",
    "competitor_url": "https://competitor.com",
    "comparison_summary": "Short comparison",
    "recommendations": [
        {
            "category": "SEO",
            "priority": "high",
            "recommendation": "Improve meta tags",
            "expected_impact": "Increase traffic by 20%"
        }
    ],
    "action_plan": [
        "1. Optimize meta tags",
        "2. Improve heading structure",
        "3. Improve page load speed"
    ],
    "overall_scores": {
        "site1": 75,
        "site2": 68
    },
    "winner_by_category": {
        "seo": "site1",
        "text_quality": "site2",
        "convenience": "site1"
    },
    "competitive_analysis": "Detailed competitive analysis"
}
```

### POST /analyze_single_site

Analyze a single website.

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
    "raw_data": {
        "seo_analysis": {...},
        "text_analysis": {...},
        "convenience_analysis": {...}
    },
    "gpt5_analysis": {
        "analysis": {
            "overall_score": 78,
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }
    },
    "overall_score": 78,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}
```

### GET /service_status

Check status of all microservices.

**Response:**
```json
{
    "overall_status": "online",
    "services": {
        "seo_service": {
            "status": "online",
            "url": "http://localhost:8001",
            "response_time": "0.05s"
        },
        "text_service": {
            "status": "online",
            "url": "http://localhost:8002",
            "response_time": "0.03s"
        },
        "convenience_service": {
            "status": "online",
            "url": "http://localhost:8003",
            "response_time": "0.07s"
        }
    },
    "timestamp": 1640995200.0
}
```

### GET /health

Service health check.

## GPT-5 agents

The service uses a specialized GPT-5 agent:

- **SeniorAnalysisAgent** — senior web analytics expert
- Aggregates results from all microservices
- Generates strategic recommendations
- Produces a prioritized action plan
- Performs competitive analysis

## Microservice integration

The service orchestrates:

- **SEO_analyses** (port 8001) — SEO analysis
- **Text_analyses** (port 8002) — text/content analysis
- **Convenience_analyses** (port 8003) — UX analysis

## Workflow

1. **Data collection** — parallel requests to all microservices
2. **Aggregation** — merge analysis results
3. **GPT-5 analysis** — comparative reasoning
4. **Recommendations** — generate a prioritized improvement plan
5. **Response** — return the result

## Monitoring and diagnostics

The service provides:

- Status checks for all microservices
- Response-time monitoring
- Connection error handling
- Operation logging

## Error handling

The service handles:

- Microservice unavailability
- GPT-5 API errors
- Request timeouts
- Parsing errors
- Input validation errors

## Performance

- Async request handling
- Parallel microservice calls
- Caching of analysis results
- Optimized processing for large payloads

## Security

- Input URL validation
- Request time limits
- Error handling without leaking internal details
- Audit-friendly logging
