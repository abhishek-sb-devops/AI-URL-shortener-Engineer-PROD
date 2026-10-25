from __future__ import annotations

import logging
import sys
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse

from src.config import settings
from src.exceptions import (
    AliasConflictException,
    AnalyticsAuthenticationRequired,
    AnalyticsAuthenticationUnavailable,
    InvalidClientAddress,
    InvalidURLSchemeException,
    RateLimitExceeded,
    RateLimitUnavailable,
    URLNotFoundException,
)
from src.models import AnalyticsResponse, ErrorResponse, ShortenRequest, ShortenResponse
from src.ratelimit import RateLimiter
from src.repository import SQLiteRepository, get_repository
from src.service import URLShortenerService

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("app")

repo = get_repository(settings.database_url)
service = URLShortenerService(repository=repo)
rate_limiter = RateLimiter()

app = FastAPI(
    title=settings.app_name,
    version="1.2.0",
    description="Production-ready URL Shortener Microservice",
)


@app.middleware("http")
async def request_correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    logger.info("Incoming Request [%s] %s %s", correlation_id, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = correlation_id
    logger.info("Completed Request [%s] Status: %d", correlation_id, response.status_code)
    return response


@app.middleware("http")
async def enforce_rate_limits(request: Request, call_next):
    if not settings.enable_rate_limits:
        return await call_next(request)

    category = None
    if request.method == "POST" and request.url.path == "/api/v1/shorten":
        category = "create"
    elif request.method == "GET" and request.url.path.startswith("/api/v1/analytics/"):
        category = "analytics"
    elif request.method == "GET" and request.url.path.count("/") == 1 and request.url.path != "/":
        category = "redirect"

    if category is None:
        return await call_next(request)

    try:
        await rate_limiter.enforce(request, category)
    except InvalidClientAddress as exc:
        return JSONResponse(
            status_code=400,
            content={"error": ErrorResponse(code="invalid_client_address", message=exc.message, details=None).model_dump()},
        )
    except RateLimitExceeded as exc:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(exc.retry_after_seconds)},
            content={"error": ErrorResponse(code="rate_limit_exceeded", message=exc.message, details=None).model_dump()},
        )
    except RateLimitUnavailable as exc:
        return JSONResponse(
            status_code=503,
            content={"error": ErrorResponse(code="rate_limit_unavailable", message=exc.message, details=None).model_dump()},
        )
    return await call_next(request)


@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["Health"])
def liveness_probe():
    return {"status": "healthy", "service": settings.app_name}


@app.get("/readyz", status_code=status.HTTP_200_OK, tags=["Health"])
def readiness_probe():
    try:
        repo.check_health()
        return {"status": "ready", "storage": "sqlite_connected"}
    except Exception as exc:
        logger.error("Readiness check failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage connection failed",
        ) from exc


@app.get("/health/live", status_code=status.HTTP_200_OK, tags=["Health"])
def health_live():
    return {"status": "alive"}


@app.get("/health/ready", status_code=status.HTTP_200_OK, tags=["Health"])
def health_ready():
    try:
        repo.check_health()
        dependencies = {
            "postgres": settings.database_url.startswith("postgresql"),
            "redis": True,
            "analytics_authentication": bool(settings.analytics_api_key),
        }
        return {"status": "ready", "dependencies": dependencies}
    except Exception as exc:
        logger.error("health ready failed: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "dependencies": {
                    "postgres": False,
                    "redis": False,
                    "analytics_authentication": bool(settings.analytics_api_key),
                },
            },
        )


@app.post(
    "/api/v1/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["URL Operations"],
)
def shorten_url(payload: ShortenRequest):
    try:
        record = service.shorten_url(
            original_url=str(payload.original_url),
            custom_alias=payload.custom_alias,
        )
        return record
    except AliasConflictException as exc:
        logger.warning("Alias Conflict: %s", exc.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except InvalidURLSchemeException as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc


@app.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    tags=["URL Operations"],
)
def redirect_to_url(short_code: str):
    try:
        target_url = service.resolve_url(short_code)
        return RedirectResponse(url=target_url, status_code=status.HTTP_302_FOUND)
    except URLNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@app.get(
    "/api/v1/analytics/{short_code}",
    response_model=AnalyticsResponse,
    tags=["Analytics"],
)
def get_analytics(short_code: str, request: Request):
    if settings.analytics_api_key is not None:
        header_value = request.headers.get("Authorization", "")
        expected = f"Bearer {settings.analytics_api_key}"
        if header_value != expected:
            raise AnalyticsAuthenticationRequired("A valid bearer token is required.")

    try:
        record = service.get_analytics(short_code)
        return {
            "short_code": record["short_code"],
            "original_url": record["original_url"],
            "created_at": record["created_at"],
            "total_clicks": record["clicks"],
        }
    except URLNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@app.exception_handler(URLNotFoundException)
async def handle_url_not_found(request: Request, exc: URLNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": ErrorResponse(code="url_not_found", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(AliasConflictException)
async def handle_alias_conflict(request: Request, exc: AliasConflictException):
    return JSONResponse(
        status_code=400,
        content={"error": ErrorResponse(code="alias_conflict", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(InvalidURLSchemeException)
async def handle_invalid_url(request: Request, exc: InvalidURLSchemeException):
    return JSONResponse(
        status_code=422,
        content={"error": ErrorResponse(code="invalid_url", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(AnalyticsAuthenticationRequired)
async def handle_analytics_auth_required(request: Request, exc: AnalyticsAuthenticationRequired):
    return JSONResponse(
        status_code=401,
        content={"error": ErrorResponse(code="authentication_required", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(AnalyticsAuthenticationUnavailable)
async def handle_analytics_auth_unavailable(request: Request, exc: AnalyticsAuthenticationUnavailable):
    return JSONResponse(
        status_code=503,
        content={"error": ErrorResponse(code="authentication_not_configured", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(RateLimitExceeded)
async def handle_rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(exc.retry_after_seconds)},
        content={"error": ErrorResponse(code="rate_limit_exceeded", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(RateLimitUnavailable)
async def handle_rate_limit_unavailable(request: Request, exc: RateLimitUnavailable):
    return JSONResponse(
        status_code=503,
        content={"error": ErrorResponse(code="rate_limit_unavailable", message=exc.message, details=None).model_dump()},
    )


@app.exception_handler(InvalidClientAddress)
async def handle_invalid_client_address(request: Request, exc: InvalidClientAddress):
    return JSONResponse(
        status_code=400,
        content={"error": ErrorResponse(code="invalid_client_address", message=exc.message, details=None).model_dump()},
    )


__all__ = ["app", "repo", "service"]
