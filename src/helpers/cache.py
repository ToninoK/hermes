from redis import Redis

from src.config import Config


class Cache:
    def __init__(self, namespace):
        self.namespace = namespace
        self.redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
        self.ttl = 24 * 60 * 60

    def set(self, key, value, ttl):
        return self.redis.set(
            f"{self.namespace}:{key}", value, keepttl=(ttl or self.ttl)
        )

    def get(self, key):
        return self.redis.get(f"{self.namespace}:{key}")
