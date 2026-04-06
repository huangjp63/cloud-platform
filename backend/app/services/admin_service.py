from sqlalchemy.orm import Session
from app.models.user import User
from app.models.file import File
from app.services.user_service import UserService
from app.services.file_service import FileService
from app.dependencies import delete_user_cache
from app.utils.file_utils import format_file_size
from datetime import datetime, timedelta


class AdminService:
    def get_all_users(self, db: Session) -> list:
        users = db.query(User).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None
            }
            for user in users
        ]
    
    def get_total_statistics(self, db: Session) -> dict:
        total_files = db.query(File).filter(File.is_deleted == 0).count()
        total_size = db.query(File).filter(File.is_deleted == 0).with_entities(File.size).all()
        total_size = sum([size[0] or 0 for size in total_size])
        
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_active_users = db.query(User).filter(User.last_login_time >= today_start).count()
        
        return {
            "total_users": db.query(User).count(),
            "total_files": total_files,
            "total_size": format_file_size(total_size),
            "today_active_users": today_active_users
        }
    
    def get_all_files(self, db: Session) -> list:
        files = db.query(File).filter(File.is_deleted == 0).all()
        result = []
        for file in files:
            user = db.query(User).filter(User.id == file.user_id).first()
            result.append({
                "id": file.id,
                "filename": file.name,
                "username": user.username if user else "未知用户",
                "size": file.size,
                "upload_time": file.create_time.strftime("%Y-%m-%d %H:%M:%S") if file.create_time else None
            })
        return result
    
    def delete_user(self, db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.role != "admin":
            db.delete(user)
            db.commit()
            delete_user_cache(user_id)
            return True
        return False
    
    def update_user_role(self, db: Session, user_id: int, role: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = role
            db.commit()
            db.refresh(user)
            
            user_dict = {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None,
                "last_login_time": user.last_login_time.strftime("%Y-%m-%d %H:%M:%S") if user.last_login_time else None
            }
            from app.dependencies import set_user_cache
            set_user_cache(user_id, user_dict, expire=3600)
            return True
        return False
    
    def delete_file(self, db: Session, file_id: int) -> bool:
        file = db.query(File).filter(File.id == file_id).first()
        if file:
            file.is_deleted = 1
            db.commit()
            return True
        return False

