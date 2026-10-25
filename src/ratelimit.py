from __future__ import annotations

import ipaddress

from fastapi import Request
from redis import Redis
from redis.exceptions import RedisError

from src.config import settings
from src.exceptions import InvalidClientAddress, RateLimitExceeded, RateLimitUnavailable


class RateLimiter:
    def __init__(self, redis_client: Redis | None = None):
        self.redis_client = redis_client

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            values = [part.strip() for part in forwarded_for.split(",") if part.strip()]
            if values:
                candidate = values[0]
                try:
                    ipaddress.ip_address(candidate)
                    return candidate
                except ValueError:
                    pass

        client = request.client.host if request.client else "127.0.0.1"

        if client in {"127.0.0.1", "localhost", "::1", "testclient"}:
            return "127.0.0.1"

        try:
            ipaddress.ip_address(client)
            return client
        except ValueError as exc:
            raise InvalidClientAddress(
                "Client address could not be determined safely"
            ) from exc

    async def enforce(self, request: Request, category: str) -> None:
        if not settings.enable_rate_limits:
            return

        try:
            client_ip = self._get_client_ip(request)
            if self.redis_client is None:
                self.redis_client = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                )

            limits = {
                "create": settings.rate_limit_create_per_minute,
                "redirect": settings.rate_limit_redirect_per_minute,
                "analytics": settings.rate_limit_analytics_per_minute,
            }
            limit = limits.get(category, 60)
            key = f"rate-limit:{category}:{client_ip}"
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, 60)
            if current > limit:
                raise RateLimitExceeded(
                    "Request rate limit exceeded",
                    retry_after_seconds=60,
                )
        except RedisError as exc:
            raise RateLimitUnavailable(
                "Rate-limit service is temporarily unavailable"
            ) from exc


def get_client_ip(request: Request) -> str:
    return RateLimiter()._get_client_ip(request)
