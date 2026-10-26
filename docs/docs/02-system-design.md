# System Design

## Summary

This service is a lightweight URL shortener with:
- a FastAPI web layer
- a repository layer for persistence
- a service layer for business logic
- optional Redis-based rate limiting
- optional analytics protection

## High-level components

### 1. API layer
FastAPI is used as the web framework. It exposes:
- shorten endpoint
- redirect endpoint
- analytics endpoint
- health and readiness endpoints

### 2. Service layer
`URLShortenerService` owns:
- URL validation
- custom alias validation
- short-code generation
- click increment logic
- analytics retrieval

### 3. Repository layer
The repository layer abstracts persistence. It supports:
- SQLite for local/dev execution
- Postgres-ready architecture for deployment scenarios
- access to redirect records and analytics data

### 4. Rate limiting layer
Redis-backed rate limiting enforces request quotas by category:
- create requests
- redirect requests
- analytics requests

### 5. Configuration layer
`src/config.py` provides environment-driven configuration for:
- database URL
- Redis URL
- analytics API key
- rate limit settings
- trusted proxy list

## Request flow

### Shorten flow
1. Client sends `POST /api/v1/shorten`
2. Service validates original URL
3. Service checks alias uniqueness if custom alias is provided
4. Service saves the original URL and generated short code
5. API responds with short code metadata

### Redirect flow
1. Client requests `/{short_code}`
2. Service resolves the code
3. Repository returns the destination URL
4. Redirect response is issued to client

### Analytics flow
1. Client requests `/api/v1/analytics/{short_code}`
2. If analytics auth is configured, bearer token is required
3. Service fetches analytics and returns click count and metadata

## Design choices

- SQLite-first for low-friction local development
- Postgres-ready abstraction for future deployment alignment
- Redis for rate limiting rather than in-memory application state
- environment-based configuration for operational flexibility
- explicit error handling for invalid URLs, duplicate aliases, and not-found conditions

## Scalability and deployment considerations

This design is sufficient for a small-to-medium deployment profile, but it is not a fully production-hardened public internet system. Production deployment would require:
- TLS termination and proxy configuration
- secure secret handling
- backup strategy
- logs and metrics
- operational runbooks
- deployment rollout/rollback model

## Summary

The design is simple, understandable, and aligned with the assignment goals: create a shortener, validate functionality, and build enough operational awareness that the project could be discussed as a production-style implementation.
