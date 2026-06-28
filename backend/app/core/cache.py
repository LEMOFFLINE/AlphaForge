import json
from typing import Any

import redis
from redis.exceptions import RedisError

from app.core.config import settings


class CacheClient:
    """Small Redis wrapper with graceful failure for local development."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: redis.Redis | None = None
        self._available = True

    @property
    def client(self) -> redis.Redis | None:
        if not self._available:
            return None

        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                )
                self._client.ping()
            except (RedisError, OSError):
                self._available = False
                self._client = None

        return self._client

    def get_json(self, key: str) -> Any | None:
        client = self.client
        if client is None:
            return None

        try:
            raw_value = client.get(key)
            return json.loads(raw_value) if raw_value else None
        except (RedisError, OSError, json.JSONDecodeError):
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        client = self.client
        if client is None:
            return

        try:
            payload = json.dumps(value)
            client.set(key, payload, ex=ttl_seconds)
        except (RedisError, OSError, TypeError):
            return

    def healthcheck(self) -> bool:
        client = self.client
        if client is None:
            return False

        try:
            return bool(client.ping())
        except (RedisError, OSError):
            return False

    def close(self) -> None:
        if self._client is not None:
            self._client.close()


cache_client = CacheClient(settings.REDIS_URL)
