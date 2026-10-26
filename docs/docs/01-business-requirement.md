# Business Requirement

## Objective

Build a URL shortener service that accepts a destination URL, generates a short code, and redirects users to the original destination. The service must also support custom aliases, basic analytics, and deployment-ready configuration patterns.

## Functional requirements

1. Create a short URL from an original URL
2. Support optional custom alias
3. Redirect a short code to the destination URL
4. Track click counts
5. Expose analytics for a short code
6. Provide health and readiness endpoints
7. Safeguard invalid URLs and duplicate aliases
8. Support local SQLite execution and Postgres-ready deployment structure

## Non-functional requirements

1. Local developer workflow must be simple
2. CI validation must be stable
3. The project must support production-style settings
4. Rate limiting and auth controls should be environment-driven
5. The repository should be suitable for assessment and review
6. The code should be structured for secure and operationally aware deployment discussions

## Assumptions

- The app is an internal or semi-public service, not necessarily an internet-wide public platform
- Local execution uses SQLite by default
- Production-style execution may use PostgreSQL and Redis
- Private analytics access is protected by a bearer token when configured
- The primary goal is correctness, validation, and deployment-readiness framing

## Acceptance criteria

The solution is considered successful if:
- a URL can be shortened
- a short code redirects correctly
- duplicate aliases are rejected cleanly
- click counting works
- the app exposes readiness and health probes
- the test suite passes
- the CI pipeline validates both SQLite and Postgres-oriented scenarios

## Out of scope for this version

- full public production release
- enterprise admin controls
- per-link user authorization
- fleet monitoring and production dashboards
- real secret manager integration
- full backup/restore automation
- large-scale load test certification
