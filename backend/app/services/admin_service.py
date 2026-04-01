from sqlalchemy.orm import Session
from app.models.user import User


class AdminService:
    def get_all_users(self, db: Session) -> list:
        users = db.query(User).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            for user in users
        ]
    
    def get_total_statistics(self, db: Session) -> dict:
        return {
            "total_users": db.query(User).count(),
            "total_files": 0,
            "total_size": 0,
            "today_active_users": 0
        }
