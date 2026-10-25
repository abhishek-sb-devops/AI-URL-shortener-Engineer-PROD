# AI-Assisted Software Engineering — URL Shortener Service

[![CI Quality Gate](https://github.com/abhishek-sb-devops/ai-proficient-se/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishek-sb-devops/ai-proficient-se/actions)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)
![Code Style](https://img.shields.io/badge/code%20style-flake8-green)
![Tests](https://img.shields.io/badge/tests-pytest-brightgreen)

A hardened URL shortener service built with Python, FastAPI, and a production-oriented configuration model. The project supports custom aliases, redirect flows, analytics reads, optional analytics authentication, and operational controls such as request correlation, dependency-aware health checks, and Redis-backed rate limiting when enabled.

## Architecture summary

This repository is intentionally positioned as a practical production-style URL shortener foundation:

- FastAPI service with redirect and analytics endpoints
- SQLite repository for local/default execution with WAL durability
- Postgres-aware repository scaffolding and Alembic migration setup for deployment readiness
- Redis-backed rate limiting and client IP validation helpers
- Optional analytics bearer-token protection via environment configuration
- Structured logging and request correlation middleware
- Environment-driven settings for deployment and local operation

## Repository structure

```text
ai-proficient-se/
├── .env.example                 # Environment-based config template
├── .github/
│   └── workflows/
│       └── ci.yml               # CI workflow
├── alembic/                     # Migration scaffolding and configuration
│   ├── env.py
│   ├── versions/
│   └── ...
├── src/
│   ├── __init__.py
│   ├── analytics_worker.py      # Redis-backed analytics worker stub
│   ├── config.py               # Pydantic settings and environment config
│   ├── encoder.py              # Base62 code generation utility
│   ├── exceptions.py            # Domain-specific exceptions
│   ├── main.py                 # FastAPI application entrypoint
│   ├── middleware.py           # Request correlation middleware
│   ├── models.py               # Request/response schemas
│   ├── ratelimit.py            # Redis-backed rate limiting logic
│   ├── repository.py           # SQLite repository + Postgres-ready abstraction
│   └── service.py              # URL shortening and resolution logic
├── tests/
│   ├── test_api.py             # API integration tests
│   └── test_service.py         # Unit tests
├── AI_DOCUMENTATION.md
├── Dockerfile
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Features

- Create short links with optional custom aliases
- Resolve short codes via redirect response
- Record click counts in storage
- Support analytics retrieval for a short code
- Health and readiness route checks
- Request correlation IDs in headers
- Validation for invalid destination URLs and alias conflicts
- Environment configuration via `.env` and `pydantic-settings`
- Optional analytics auth via bearer token
- Redis-backed rate limiting when `ENABLE_RATE_LIMITS=true`
- Postgres-ready repository and Alembic migration scaffolding for operational upgrades

## Prerequisites

- Python 3.11+
- Optional: PostgreSQL and Redis for production-like deployment tests
- Optional: Docker for containerized runs

## Local setup

Clone the repository:

```bash
git clone https://github.com/abhishek-sb-devops/ai-proficient-se.git
cd ai-proficient-se
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate # Windows
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create an environment file from the example:

```bash
cp .env.example .env
```

Review and adjust values such as:

- `DATABASE_URL`
- `REDIS_URL`
- `ANALYTICS_API_KEY`
- `ENABLE_RATE_LIMITS`
- `TRUSTED_PROXY_CIDRS`

## Running the app

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/docs
- http://localhost:8000/healthz
- http://localhost:8000/readyz

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/healthz` | Liveness check |
| `GET` | `/readyz` | Readiness check |
| `GET` | `/health/live` | Lightweight process liveness |
| `GET` | `/health/ready` | Dependency-aware readiness |
| `POST` | `/api/v1/shorten` | Create a short code |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/api/v1/analytics/{short_code}` | Fetch analytics for a short code |

Example shorten request:

```bash
curl -X POST http://localhost:8000/api/v1/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com"}'
```

Example analytics request with bearer auth:

```bash
curl -H "Authorization: Bearer change-me-to-a-long-random-secret" \
  http://localhost:8000/api/v1/analytics/<short_code>
```

## Operational controls

This repository includes several operational hardening patterns that align with a production-style service:

- Request correlation middleware emits `X-Request-ID`
- Health and readiness endpoints distinguish process health from dependency health
- Optional bearer authentication protects analytics access
- Redis-based per-client rate limiting can be enabled with environment config
- Trusted proxy configuration is supported for forwarded IP handling
- Postgres-ready repository layer and Alembic scaffolding support future migration-driven deployment

## Testing

Run the project tests:

```bash
pytest -q
```

For linting:

```bash
flake8 src tests --max-line-length=100
```

## Notes

This project is a hardened, operationally aware URL shortener foundation rather than a single-purpose toy implementation. It supports local SQLite use and includes the scaffolding needed for PostgreSQL/Redis-oriented deployment patterns while maintaining a testable FastAPI interface.

The service remains suitable for local development and incremental production hardening, and the codebase is intentionally structured to support that progression.


























































































































































































































































































































































































