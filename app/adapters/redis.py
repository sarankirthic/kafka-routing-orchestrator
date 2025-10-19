from redis import Redis
from flask import current_app


class RedisAdapter:
    """Manages Redis connections and common caching/locking operations."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = None

    def init_app(self, app=None):
        """Initialize a pooled Redis client."""
        url = app.config.get("REDIS_URL", self.redis_url)
        self.client = Redis.from_url(url, decode_responses=True)
        return self

    @classmethod
    def from_current_app(cls):
        """Construct Redis adapter from active Flask app context."""
        conf = current_app.config
        adapter = cls(conf["REDIS_URL"])
        adapter.init_app(current_app)
        return adapter

    # Common helper patterns
    def hset_json(self, key: str, mapping: dict, ttl: int = 300):
        """Set a hash with optional expiry."""
        self.client.hset(key, mapping=mapping)
        if ttl:
            self.client.expire(key, ttl)

    def get_json_hash(self, key: str) -> dict:
        """Fetch hash and return as dictionary."""
        return self.client.hgetall(key)

    def acquire_lock(self, key: str, ttl: int = 30) -> bool:
        """Simple distributed lock via SETNX."""
        return bool(self.client.set(name=f"lock:{key}", value="1", nx=True, ex=ttl))

    def release_lock(self, key: str):
        """Release distributed lock."""
        self.client.delete(f"lock:{key}")
