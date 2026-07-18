import json
import redis
from typing import Optional
from .config import REDIS_URL


class RedisManager:
    def __init__(self):
        self.redis = None
        self.connected = False
        try:
            self.redis = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
            self.redis.ping()
            self.connected = True
        except Exception:
            self.connected = False

    def get_client(self):
        return self.redis

    def cache_set(self, key: str, value, expire: int = 300):
        if not self.connected:
            return
        try:
            self.redis.setex(key, expire, json.dumps(value, default=str))
        except Exception:
            pass

    def cache_get(self, key: str):
        if not self.connected:
            return None
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    def cache_delete(self, key: str):
        if not self.connected:
            return
        try:
            self.redis.delete(key)
        except Exception:
            pass

    def cache_delete_pattern(self, pattern: str):
        if not self.connected:
            return
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception:
            pass

    def publish(self, channel: str, message: dict):
        if not self.connected:
            return
        try:
            self.redis.publish(channel, json.dumps(message, default=str))
        except Exception:
            pass

    def subscribe(self, *channels):
        if not self.connected:
            return None
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(*channels)
            return pubsub
        except Exception:
            return None

    def increment_rate_limit(self, key: str, window: int = 60) -> int:
        if not self.connected:
            return 0
        try:
            count = self.redis.incr(key)
            if count == 1:
                self.redis.expire(key, window)
            return count
        except Exception:
            return 0

    def get_rate_limit(self, key: str) -> int:
        if not self.connected:
            return 0
        try:
            count = self.redis.get(key)
            return int(count) if count else 0
        except Exception:
            return 0


redis_manager = RedisManager()
