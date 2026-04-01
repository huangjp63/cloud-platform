from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.utils.redis_client import redis_client
import json

security = HTTPBearer()


def get_user_from_cache(user_id: int) -> dict:
    """从 Redis 缓存获取用户信息"""
    cache_key = f"user:{user_id}"
    user_data = redis_client.get(cache_key)
    return user_data


def set_user_cache(user_id: int, user_data: dict, expire: int = 3600):
    """将用户信息缓存到 Redis"""
    cache_key = f"user:{user_id}"
    redis_client.set(cache_key, user_data, expire=expire)


def delete_user_cache(user_id: int):
    """删除用户缓存"""
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)


def user_to_dict(user: User) -> dict:
    """将 User 对象转换为字典"""
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "create_time": user.create_time.isoformat() if user.create_time else None,
        "last_login_time": user.last_login_time.isoformat() if user.last_login_time else None
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户（支持缓存）"""
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )
    
    user_id = int(user_id)
    
    # 1. 尝试从缓存获取用户信息
    cached_user = get_user_from_cache(user_id)
    if cached_user:
        # 将缓存数据转换为 User 对象
        user = User(
            id=cached_user["id"],
            username=cached_user["username"],
            role=cached_user["role"],
            create_time=cached_user.get("create_time"),
            last_login_time=cached_user.get("last_login_time")
        )
        return user
    
    # 2. 缓存未命中，从数据库查询
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    # 3. 将用户信息缓存到 Redis（1小时过期）
    user_dict = user_to_dict(user)
    set_user_cache(user_id, user_dict, expire=3600)
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


def refresh_user_cache(user_id: int, db: Session):
    """刷新用户缓存（用户信息变更时调用）"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user_dict = user_to_dict(user)
        set_user_cache(user_id, user_dict, expire=3600)
    else:
        delete_user_cache(user_id)
