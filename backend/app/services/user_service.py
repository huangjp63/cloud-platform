from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password
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
        return user
    
    def update_last_login(self, db: Session, user: User) -> None:
        user.last_login_time = datetime.now()
        db.commit()
