from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from app.dependencies import set_user_cache, delete_user_cache, user_to_dict
from datetime import datetime


class UserService:
    def get_user_by_username(self, db: Session, username: str) -> User:
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            password=hash_password(user_data.password),
            role="user"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 将新用户缓存到 Redis
        user_dict = user_to_dict(user)
        set_user_cache(user.id, user_dict, expire=3600)
        
        return user
    
    def update_last_login(self, db: Session, user: User) -> None:
        user.last_login_time = datetime.now()
        db.commit()
        
        # 更新用户缓存
        user_dict = user_to_dict(user)
        set_user_cache(user.id, user_dict, expire=3600)
    
    def update_user_role(self, db: Session, user_id: int, role: str) -> User:
        """更新用户角色"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = role
            db.commit()
            db.refresh(user)
            
            # 刷新用户缓存
            user_dict = user_to_dict(user)
            set_user_cache(user_id, user_dict, expire=3600)
        return user
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        """删除用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            
            # 删除用户缓存
            delete_user_cache(user_id)
            return True
        return False

    def update_password(self, db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """更新用户密码"""
        user = db.query(User).filter(User.id == user_id).first()
        if user and verify_password(old_password, user.password):
            user.password = hash_password(new_password)
            db.commit()

            # 清除用户缓存，强制重新登录
            delete_user_cache(user_id)
            return True
        return False
