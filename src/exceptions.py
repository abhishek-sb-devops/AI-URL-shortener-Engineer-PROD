from __future__ import annotations


class DomainException(Exception):
    """Base exception for all domain-specific errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class URLNotFoundException(DomainException):
    """Raised when a short code does not exist in the repository."""


class AliasConflictException(DomainException):
    """Raised when a requested custom alias is already occupied."""


class InvalidURLSchemeException(DomainException):
    """Raised when the URL scheme is unsupported or invalid."""


class AnalyticsAuthenticationRequired(DomainException):
    """Raised when analytics access is requested without valid credentials."""


class AnalyticsAuthenticationUnavailable(DomainException):
    """Raised when analytics auth is not configured in the environment."""


class RateLimitExceeded(DomainException):
    def __init__(self, message: str, retry_after_seconds: int = 60):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(message)


class RateLimitUnavailable(DomainException):
    """Raised when the backing rate-limit service is unavailable."""


class InvalidClientAddress(DomainException):
    """Raised when the client IP cannot be safely determined."""
