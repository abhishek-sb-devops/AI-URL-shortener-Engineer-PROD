# AI URL Shortener Engineer PROD

A production-style URL shortener service built with FastAPI, SQLite-first local execution, Postgres-ready repository abstraction, Redis-backed rate limiting, and operational health checks.

This repository is structured for:
- local development and testing
- CI validation
- deployment-readiness discussion
- environment-based configuration
- operational hardening evaluation

## Overview

This project implements the following:
- generating short URLs from original URLs
- optional custom aliases
- redirect resolution
- click tracking
- analytics retrieval
- health and readiness endpoints
- configuration via environment variables
- SQLite default mode with Postgres-ready architecture
- Redis-backed rate limiting support
- optional analytics bearer-token protection

The service is intentionally built as a production-style foundation, not as a disposable toy example.

## Architecture

- API layer: FastAPI
- Storage:
  - SQLite by default for local/dev execution
  - Postgres-ready repository abstraction for production-style deployment
- Rate limiting: Redis
- Config: Pydantic Settings
- Validation: pytest
- Linting: flake8
- CI: GitHub Actions

## Repository layout

```text
AI-URL-shortener-Engineer-PROD/
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── docs/
│   ├── 01-business-requirement.md
│   ├── 02-system-design.md
│   ├── 03-engineering-design.md
│   ├── 04-engineering-breakdown.md
│   └── 05-risk-assumptions-database-design.md
├── evidence/
│   ├── README.md
│   ├── greenfield/
│   ├── brownfield/
│   └── ambiguous/
├── src/
│   ├── config.py
│   ├── encoder.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models.py
│   ├── ratelimit.py
│   ├── repository.py
│   └── service.py
├── tests/
│   ├── test_api.py
│   └── test_service.py
├── AI_DOCUMENTATION.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
└── .env
