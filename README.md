# AI URL Shortener Engineer PROD

A production-style URL shortener service built with FastAPI, SQLite-first local execution, Postgres-ready repository abstraction, Redis-backed rate limiting, and operational health checks.

This project is designed to demonstrate a realistic engineering workflow:
- building a working service
- validating behavior with tests
- improving operational readiness
- documenting architecture and evidence
- being explicit about what is still not production-certified

## Why this project exists

This repository implements a basic URL shortener service with:
- short code generation
- redirect handling
- optional custom aliases
- click tracking
- analytics access
- health and readiness endpoints
- local SQLite execution
- Postgres-ready architecture
- Redis-backed rate limiting
- production-style configuration

The goal is not just to create a shortener, but to show a practical engineering progression:
- greenfield implementation
- correctness fixes
- operational hardening
- CI stabilization
- evidence and documentation improvement

## Project status

This repository is best described as:
- a production-style foundation
- a credible engineering implementation
- suitable for assessment and review
- not yet a fully production-certified public deployment

It includes real implementation and validation work, but it still requires additional operational work before public production rollout.

## Architecture summary

This service is built around a simple layered architecture:

- API layer: FastAPI
- Business logic: service layer
- Data access: repository layer
- Persistence:
  - SQLite by default for local execution
  - Postgres-ready abstraction for production-style deployment
- Rate limiting: Redis
- Config: environment-driven settings
- Validation: pytest
- Linting: flake8
- CI: GitHub Actions

## Main components

- `src/main.py`
  - FastAPI application entry point
- `src/service.py`
  - shortener logic
  - redirect logic
  - alias validation
  - click tracking
- `src/repository.py`
  - storage logic
  - persistence abstraction
- `src/config.py`
  - environment-driven configuration
- `src/ratelimit.py`
  - Redis-backed rate limiting
- `src/models.py`
  - request/response schemas
- `src/encoder.py`
  - short-code generation
- `src/exceptions.py`
  - domain-specific exceptions

## Features

- create short URLs from original URLs
- generate deterministic short codes
- support custom aliases
- redirect short codes to destination URLs
- count clicks
- expose analytics endpoints
- validate invalid URLs and duplicate aliases
- health and readiness probes
- request correlation IDs
- environment-based configuration
- SQLite fallback for local execution
- Postgres-ready repository abstraction
- Redis-based rate limiting
- optional analytics authentication via bearer token

## Repository structure

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
├── .env.example
└── .env
