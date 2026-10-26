# Risks, Assumptions, and Database Design

## Key risks

### 1. URL validity and abuse
The service accepts user-provided destinations. Without additional controls, it may be abused to redirect users to unsafe or undesirable destinations.

Mitigation:
- validate scheme and address structure
- restrict to http/https
- document trusted-proxy assumptions
- enforce secure deployment assumptions

### 2. Alias collisions
Custom aliases introduce the risk of duplicate short codes.

Mitigation:
- validate alias format
- enforce uniqueness at repository layer
- fail with clear domain error

### 3. Operational failures
The service may encounter:
- Redis outage
- Postgres outage
- invalid proxy headers
- config drift
- rate-limit service issues

Mitigation:
- readiness checks
- graceful degradation patterns
- environment-specific configuration
- operational monitoring recommendations

### 4. Secret handling
Sensitive values must not be committed to source control.

Mitigation:
- use environment variables
- keep `.env` out of version control
- document secret rotation requirements
- externalize to real secret management for production use

## Assumptions

- The application is a medium-scale service, not a globally distributed system
- Local execution uses SQLite for simplicity
- Production-style environments may use Postgres and Redis
- Short codes are deterministic and short enough for user convenience
- Analytics auth is optional and environment-driven
- Public production deployment requires additional operational controls not yet fully specified in this repo

## Database design overview

The application uses a simple persistence model centered on:
- short URL records
- generated code
- original target URL
- timestamps
- click tracking

### Data model expectations
The repository stores:
- short_code
- original_url
- created_at
- click_count or equivalent analytics representation

These values are sufficient for:
- redirect behavior
- basic analytics retrieval
- custom alias uniqueness
- simple operational validation

## Storage decisions

### SQLite
Used for:
- local testing
- CI execution
- simple developer workflows

Benefits:
- easy to run
- no external service required
- fast local iteration

### Postgres-ready abstraction
Used to signal:
- planning for real deployment contexts
- compatibility with more production-like infrastructure
- migration readiness

This is not a claim that full Postgres production deployment is already completed.

## Deployment risk statement

This repo is better described as:
- a production-style service foundation
- not a fully production-certified public-facing deployment

The remaining work is mostly operational maturity:
- backup/restore
- TLS and proxy assumptions
- real secret management
- load validation
- migration verification
- runbooks and response procedures

## Summary

The system is intentionally simple but operationally aware. It meets the core functional requirement of a URL shortener while also demonstrating a more realistic engineering posture than a basic demo.
