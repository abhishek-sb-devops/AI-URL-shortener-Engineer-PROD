# Greenfield Scenario AI Analysis

## Scenario
Build a URL shortener service from scratch with:
- short code generation
- redirect behavior
- optional custom alias support
- click counting
- simple API structure
- testable FastAPI application

## Goal
Create a simple but clean implementation that is maintainable and testable while following a realistic engineering structure.

## AI-assisted reasoning

The best implementation pattern is:
1. Define API contracts and data model first
2. Implement a service layer for URL creation and redirect resolution
3. Use a repository abstraction to separate storage concerns
4. Add validation for invalid destinations and duplicate aliases
5. Keep tests focused on service behavior and API flow

### Recommended architecture
- FastAPI app with endpoint definitions
- Pydantic models for request/response
- `URLShortenerService` for business logic
- repository for persistence and lookup
- Base62 encoder for deterministic short-code generation

### Design choices
- SQLite is a suitable default for local development and CI
- short code generation should be deterministic and collision-safe
- alias conflict handling should be explicit and user-friendly
- redirect resolution should preserve original destination behavior
- click tracking should be simple but testable

## Resulting implementation
The implemented repository reflects this approach:
- `src/service.py` handles business logic
- `src/repository.py` persists mappings and counters
- `src/models.py` defines request and response models
- `src/main.py` exposes API and health endpoints
- `src/encoder.py` provides Base62 generation

## Validation notes
The implementation should be checked for:
- generated codes are deterministic
- redirect resolves to correct URL
- duplicate custom alias is rejected
- invalid destination URL is rejected
- not-found short code returns 404

## Conclusion
This is a sound greenfield implementation because it prioritizes correctness, clarity, and testability while keeping the project simple enough for an assessment.
