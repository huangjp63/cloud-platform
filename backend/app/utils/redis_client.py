import redis
import json
from app.config import settings


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def set(self, key: str, value: any, expire: int = None):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)
    
    def get(self, key: str):
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def delete(self, key: str):
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key)
    
    def lpush(self, key: str, value: any):
        self.client.lpush(key, json.dumps(value) if isinstance(value, (dict, list)) else value)
    
    def lrange(self, key: str, start: int = 0, end: int = -1):
        return self.client.lrange(key, start, end)


redis_client = RedisClient()
