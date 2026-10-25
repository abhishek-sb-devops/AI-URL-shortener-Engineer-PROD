from __future__ import annotations

import json
import logging

from redis import Redis
from redis.exceptions import RedisError

from src.config import settings

logger = logging.getLogger("app.analytics_worker")


class AnalyticsWorker:
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.redis_url
        self.client = Redis.from_url(self.redis_url, decode_responses=True)

    def run_once(self) -> None:
        try:
            stream_name = "url-shortener:clicks"
            event = self.client.xadd(
                stream_name,
                {"message": json.dumps({"event": "heartbeat", "ts": "live"})},
                maxlen=100,
            )
            logger.info("Analytics worker published heartbeat event %s", event)
        except RedisError as exc:
            logger.warning("Redis unavailable for analytics worker: %s", exc)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    worker = AnalyticsWorker()
    worker.run_once()


if __name__ == "__main__":
    main()
