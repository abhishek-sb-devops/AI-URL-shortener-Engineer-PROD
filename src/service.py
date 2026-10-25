from __future__ import annotations

import logging
import threading
from urllib.parse import urlparse

from src.encoder import Base62Encoder
from src.exceptions import AliasConflictException, InvalidURLSchemeException, URLNotFoundException

logger = logging.getLogger("app.service")


class URLShortenerService:
    def __init__(self, repository):
        self.repository = repository
        self.lock = threading.Lock()

    def _sanitize_url_for_log(self, url: str) -> str:
        """Redacts query parameters and credentials to secure logs."""
        try:
            parsed = urlparse(url)
            if parsed.query or parsed.params:
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?***"
            return url
        except Exception:
            return "[REDACTED_URL]"

    def _validate_original_url(self, original_url: str) -> str:
        parsed = urlparse(original_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise InvalidURLSchemeException("Original URL must be a valid http or https URL.")
        return original_url

    def _validate_custom_alias(self, custom_alias: str) -> str:
        alias = custom_alias.strip()
        if len(alias) < 3 or len(alias) > 30:
            raise AliasConflictException("Custom alias must be between 3 and 30 characters.")
        if not alias.replace("-", "").replace("_", "").isalnum():
            raise AliasConflictException(
                "Custom alias may only contain letters, numbers, hyphens, and underscores."
            )
        return alias

    def shorten_url(self, original_url: str, custom_alias: str = None) -> dict:
        valid_url = self._validate_original_url(original_url)
        safe_url = self._sanitize_url_for_log(valid_url)

        with self.lock:
            if custom_alias:
                alias = self._validate_custom_alias(custom_alias)
                logger.info("Attempting custom alias creation: '%s'", alias)
                if self.repository.get_by_code(alias):
                    raise AliasConflictException(f"Alias '{alias}' already exists.")
                short_code = alias
            else:
                next_id = self.repository.get_next_sequence_id()
                short_code = Base62Encoder.encode(next_id)
                while self.repository.get_by_code(short_code):
                    next_id = self.repository.get_next_sequence_id()
                    short_code = Base62Encoder.encode(next_id)

            record = self.repository.save(short_code, valid_url)
            logger.info("Shortened URL: '%s' -> '%s'", safe_url, short_code)
            return record

    def resolve_url(self, short_code: str) -> str:
        logger.info("Resolving short code: '%s'", short_code)
        return self.repository.increment_clicks(short_code)

    def get_analytics(self, short_code: str) -> dict:
        logger.info("Fetching analytics for short code: '%s'", short_code)
        record = self.repository.get_analytics(short_code)
        if record is None:
            raise URLNotFoundException(f"URL code '{short_code}' not found.")
        return record
