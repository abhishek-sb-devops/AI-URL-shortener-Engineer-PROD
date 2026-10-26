# Engineering Design

## Design goals

The solution was designed to balance:
- simplicity
- correctness
- testability
- production-style structure
- local developer experience

## Key technical choices

### FastAPI
FastAPI was selected because it offers:
- straightforward API definition
- built-in validation via Pydantic
- fast iteration for local testing
- clean route and response model structure

### SQLite-first local persistence
SQLite is a pragmatic default for:
- local development
- CI validation
- assessment and review environments

This keeps the application simple while making the code easy to test.

### Postgres-ready abstraction
The repository layer is intentionally structured for future Postgres compatibility. This allows the system to demonstrate deployment awareness without forcing the local developer workflow to depend on Postgres.

### Redis-backed rate limiting
Redis is used as the rate-limit backend because it is:
- external to the app process
- suitable for request throttling
- easy to integrate into a production-like architecture

### Optional analytics auth
Analytics endpoints can be protected with a bearer token. This prevents accidental exposure while still allowing the app to be used in non-production or local execution without imposing auth requirements.

## Error handling model

The code uses domain-specific exceptions to provide clear error semantics:
- invalid URL
- alias conflict
- analytics auth required
- rate-limit exceeded
- resource not found

This keeps API behavior consistent and improves debugging.

## Observability design

The app includes:
- logging
- request correlation IDs
- readiness and health checks

This helps the service be operationally understandable without requiring a full monitoring stack from day one.

## Deployment assumptions

The repository assumes:
- environment variables configure the runtime
- Redis and Postgres are optional but available in production-like deployment
- the application may sit behind a reverse proxy or ingress
- the app is not yet fully hardened for externally trusted internet exposure

## Summary

This implementation is intentionally not overly complex. It focuses on:
- app correctness
- clean service boundaries
- infrastructure realism
- control of operational assumptions

That makes it suitable for a real engineering review while still maintaining a manageable developer footprint.
