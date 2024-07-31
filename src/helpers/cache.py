from redis import Redis

from src.config import Config

import pickle


class Cache:
    def __init__(self, namespace):
        self.namespace = namespace
        self.redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
        self.ttl = 24 * 60 * 60

    def set(self, key, value, ttl=None):
        value = pickle.dumps(value)
        return self.redis.set(
            f"{self.namespace}:{key}", value, keepttl=(ttl or self.ttl)
        )

    def get(self, key):
        data = self.redis.get(f"{self.namespace}:{key}")
        if data:
            data = pickle.loads(data)
        return data, bool(data)


acl_cache = Cache("acl")
