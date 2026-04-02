import redis
import json
from typing import Optional, Union, List, Dict, Any
from app.config import settings


class RedisClient:
    """Redis 客户端封装类"""
    
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    # ==================== String 类型操作 ====================
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """
        设置字符串类型的值
        自动将 dict/list 转换为 JSON 字符串
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif not isinstance(value, str):
            value = str(value)
        
        self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)
    
    def get(self, key: str) -> Any:
        """
        获取字符串类型的值
        自动尝试解析 JSON
        """
        value = self.client.get(key)
        if value is None:
            return None
        
        # 尝试解析 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # 如果不是 JSON，返回原始字符串
            return value
    
    def delete(self, key: str) -> bool:
        """删除键"""
        return self.client.delete(key) > 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.client.exists(key) > 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        return self.client.expire(key, seconds)
    
    def ttl(self, key: str) -> int:
        """获取键的剩余过期时间"""
        return self.client.ttl(key)
    
    # ==================== Hash 类型操作（适合存储对象） ====================
    
    def hset(self, key: str, field: str, value: Any):
        """设置哈希字段的值"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        elif not isinstance(value, str):
            value = str(value)
        self.client.hset(key, field, value)
    
    def hset_dict(self, key: str, mapping: Dict[str, Any]):
        """批量设置哈希字段"""
        # 将值全部转为字符串
        str_mapping = {}
        for k, v in mapping.items():
            if isinstance(v, (dict, list)):
                str_mapping[k] = json.dumps(v, ensure_ascii=False)
            elif not isinstance(v, str):
                str_mapping[k] = str(v)
            else:
                str_mapping[k] = v
        self.client.hset(key, mapping=str_mapping)
    
    def hget(self, key: str, field: str) -> Any:
        """获取哈希字段的值"""
        value = self.client.hget(key, field)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def hgetall(self, key: str) -> Dict[str, Any]:
        """获取哈希的所有字段和值"""
        result = self.client.hgetall(key)
        if not result:
            return {}
        
        # 尝试解析每个字段的值
        parsed = {}
        for k, v in result.items():
            try:
                parsed[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                parsed[k] = v
        return parsed
    
    def hdel(self, key: str, *fields: str) -> int:
        """删除哈希字段"""
        return self.client.hdel(key, *fields)
    
    # ==================== List 类型操作 ====================
    
    def lpush(self, key: str, *values: Any) -> int:
        """左侧插入元素"""
        str_values = []
        for v in values:
            if isinstance(v, (dict, list)):
                str_values.append(json.dumps(v, ensure_ascii=False))
            elif not isinstance(v, str):
                str_values.append(str(v))
            else:
                str_values.append(v)
        return self.client.lpush(key, *str_values)
    
    def rpush(self, key: str, *values: Any) -> int:
        """右侧插入元素"""
        str_values = []
        for v in values:
            if isinstance(v, (dict, list)):
                str_values.append(json.dumps(v, ensure_ascii=False))
            elif not isinstance(v, str):
                str_values.append(str(v))
            else:
                str_values.append(v)
        return self.client.rpush(key, *str_values)
    
    def lpop(self, key: str) -> Optional[Any]:
        """左侧弹出元素"""
        value = self.client.lpop(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def rpop(self, key: str) -> Optional[Any]:
        """右侧弹出元素"""
        value = self.client.rpop(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表范围元素"""
        values = self.client.lrange(key, start, end)
        result = []
        for v in values:
            try:
                result.append(json.loads(v))
            except (json.JSONDecodeError, TypeError):
                result.append(v)
        return result
    
    def llen(self, key: str) -> int:
        """获取列表长度"""
        return self.client.llen(key)
    
    # ==================== Set 类型操作 ====================
    
    def sadd(self, key: str, *members: Any) -> int:
        """添加集合成员"""
        str_members = []
        for m in members:
            if isinstance(m, (dict, list)):
                str_members.append(json.dumps(m, ensure_ascii=False))
            elif not isinstance(m, str):
                str_members.append(str(m))
            else:
                str_members.append(m)
        return self.client.sadd(key, *str_members)
    
    def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        members = self.client.smembers(key)
        result = set()
        for m in members:
            try:
                result.add(json.loads(m))
            except (json.JSONDecodeError, TypeError):
                result.add(m)
        return result
    
    def sismember(self, key: str, member: Any) -> bool:
        """判断成员是否在集合中"""
        if isinstance(member, (dict, list)):
            member = json.dumps(member, ensure_ascii=False)
        elif not isinstance(member, str):
            member = str(member)
        return self.client.sismember(key, member)
    
    def srem(self, key: str, *members: Any) -> int:
        """移除集合成员"""
        str_members = []
        for m in members:
            if isinstance(m, (dict, list)):
                str_members.append(json.dumps(m, ensure_ascii=False))
            elif not isinstance(m, str):
                str_members.append(str(m))
            else:
                str_members.append(m)
        return self.client.srem(key, *str_members)
    
    # ==================== Sorted Set 类型操作 ====================
    
    def zadd(self, key: str, mapping: Dict[Any, float]) -> int:
        """添加有序集合成员"""
        # 将 key 转为字符串
        str_mapping = {}
        for k, v in mapping.items():
            if isinstance(k, (dict, list)):
                str_k = json.dumps(k, ensure_ascii=False)
            elif not isinstance(k, str):
                str_k = str(k)
            else:
                str_k = k
            str_mapping[str_k] = v
        return self.client.zadd(key, str_mapping)
    
    def zrange(self, key: str, start: int, end: int, withscores: bool = False) -> List[Any]:
        """按分数从低到高获取成员"""
        result = self.client.zrange(key, start, end, withscores=withscores)
        if not withscores:
            parsed = []
            for m in result:
                try:
                    parsed.append(json.loads(m))
                except (json.JSONDecodeError, TypeError):
                    parsed.append(m)
            return parsed
        return result
    
    def zrevrange(self, key: str, start: int, end: int, withscores: bool = False) -> List[Any]:
        """按分数从高到低获取成员"""
        result = self.client.zrevrange(key, start, end, withscores=withscores)
        if not withscores:
            parsed = []
            for m in result:
                try:
                    parsed.append(json.loads(m))
                except (json.JSONDecodeError, TypeError):
                    parsed.append(m)
            return parsed
        return result
    
    def zscore(self, key: str, member: Any) -> Optional[float]:
        """获取成员的分数"""
        if isinstance(member, (dict, list)):
            member = json.dumps(member, ensure_ascii=False)
        elif not isinstance(member, str):
            member = str(member)
        return self.client.zscore(key, member)
    
    def zrem(self, key: str, *members: Any) -> int:
        """移除有序集合成员"""
        str_members = []
        for m in members:
            if isinstance(m, (dict, list)):
                str_members.append(json.dumps(m, ensure_ascii=False))
            elif not isinstance(m, str):
                str_members.append(str(m))
            else:
                str_members.append(m)
        return self.client.zrem(key, *str_members)


# 单例模式
redis_client = RedisClient()
