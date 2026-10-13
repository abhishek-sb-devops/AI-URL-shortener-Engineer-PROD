import logging
import threading
from urllib.parse import urlparse
from src.encoder import Base62Encoder
from src.exceptions import URLNotFoundException, AliasConflictException

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

    def shorten_url(self, original_url: str, custom_alias: str = None) -> dict:
        safe_url = self._sanitize_url_for_log(original_url)
        with self.lock:
            if custom_alias:
                logger.info("Attempting custom alias creation: '%s'", custom_alias)
                if self.repository.get_by_code(custom_alias):
                    raise AliasConflictException(f"Alias '{custom_alias}' already exists.")
                short_code = custom_alias
            else:
                next_id = self.repository.get_next_sequence_id()
                short_code = Base62Encoder.encode(next_id)
                while self.repository.get_by_code(short_code):
                    next_id = self.repository.get_next_sequence_id()
                    short_code = Base62Encoder.encode(next_id)

            record = self.repository.save(short_code, original_url)
            logger.info("Shortened URL: '%s' -> '%s'", safe_url, short_code)
            return record

    def resolve_url(self, short_code: str) -> str:
        logger.info("Resolving short code: '%s'", short_code)
        return self.repository.increment_clicks(short_code)

    def get_analytics(self, short_code: str) -> dict:
        logger.info("Fetching analytics for short code: '%s'", short_code)
        record = self.repository.get_by_code(short_code)
        if not record:
            raise URLNotFoundException(f"URL code '{short_code}' not found.")
        return record
