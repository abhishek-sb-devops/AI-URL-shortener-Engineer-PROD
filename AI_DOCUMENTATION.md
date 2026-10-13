# AI-Assisted Software Engineering — Execution Log & Evidence

This document records the exact requirements, AI prompts, generated outputs, and validation steps used during the development of the URL Shortener service.

---

## 1. Greenfield Scenario: Core Shortening Engine
- **Requirement:** Create a deterministic Base62 short-code generator with persistent storage and REST endpoints.
- **AI Prompt:** *"Generate a FastAPI module with a Base62 encoder, Pydantic v2 validation models, and a SQLite repository using WAL mode."*
- **Generated Output:** Base62 encoder class (`src/encoder.py`), Pydantic request/response models (`src/models.py`), and SQLite repository (`src/repository.py`).
- **Validation Evidence:** Verified via `pytest` unit tests (`tests/test_service.py`), confirming that auto-increment IDs correctly map to unique Base62 strings.

---

## 2. Brownfield Scenario: Concurrency & Database Constraint Hardening
- **Requirement:** Ensure concurrent requests for custom aliases do not corrupt state or cause unhandled server crashes across multi-process workers.
- **AI Prompt:** *"Refactor `repository.py` and `service.py` to catch database `IntegrityError` on unique primary key collisions and translate them into a controlled `AliasConflictException`."*
- **Generated Output:** Try-except block around `INSERT` statement in `SQLiteRepository.save()` raising `AliasConflictException`.
- **Validation Evidence:** Verified via `tests/test_api.py` using `ThreadPoolExecutor` simulating 5 simultaneous duplicate alias requests (resulting in 1 success [201] and 4 clean failures [400]).

---

## 3. Ambiguous Requirement Resolution: Production Security & Redaction
- **Requirement:** Prevent logging sensitive destination URLs (which may contain user tokens or PII query parameters).
- **AI Prompt:** *"Write a URL sanitization helper in `service.py` that strips query parameters and credentials before emitting log statements."*
- **Generated Output:** `_sanitize_url_for_log` method using `urllib.parse.urlparse`.
- **Validation Evidence:** Confirmed via code review and `flake8` linting that full query strings are never printed to stdout.
