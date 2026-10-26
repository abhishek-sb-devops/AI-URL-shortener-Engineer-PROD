# Engineering Breakdown

## Phase 1: Foundation

The app was initially created as a minimal URL shortener:
- FastAPI routes
- short-code generation
- URL validation
- repository persistence
- redirect resolution

This established the primary business flow.

## Phase 2: Reliability and correctness

The next phase introduced:
- custom alias validation
- duplicate alias rejection
- consistent error handling
- service-level test coverage
- API-level test coverage

This was necessary to turn the service from a prototype into something reviewable and stable.

## Phase 3: Production-style hardening

The repo was then adjusted to better resemble a real service:

- `src/config.py` introduced environment-driven configuration
- `src/ratelimit.py` introduced Redis rate limiting
- `src/main.py` added health and readiness endpoints
- request correlation and logging improvements were added
- analytics auth enforcement was introduced
- SQLite fallback and Postgres-ready architecture were clarified

This was the point where the repo moved from “basic app” to “operationally aware app.”

## Phase 4: CI stabilization

The CI workflow had to be corrected to avoid an environment mismatch:
- unit tests were written around SQLite semantics
- Postgres smoke checks were incorrectly mixed into the same workflow context

The fix separated:
- normal SQLite test flow
- dedicated Postgres smoke validation

This was a crucial engineering step because it improved the trustworthiness of the automation.

## Phase 5: Evidence and review framing

The final phase focused on improving the evidence trail:
- README was updated to match actual repo state
- AI documentation records the implementation path
- design docs explain architecture and trade-offs
- evidence folder supports requirement validation narrative

This is the layer that gives the project a more polished and credible assessment footprint.

## Summary

The implementation is not monolithic; it evolved through clearly separated stages:
1. Minimal functionality
2. correctness and validation
3. operational hardening
4. CI stabilization
5. documentation and evidence refinement

This progression is important because it shows deliberate engineering improvement rather than unstructured patching.
