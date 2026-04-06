from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.file import File
from app.models.user import User


class AnalysisService:
    def get_file_statistics(self, db: Session, user_id: int, role: str, stat_type: str) -> dict:
        return {
            "upload_count": 0,
            "total_size": 0,
            "type_distribution": {}
        }
    
    def get_behavior_statistics(self, db: Session, user_id: int, role: str, stat_type: str) -> dict:
        return {
            "login_count": 0,
            "upload_count": 0,
            "download_count": 0,
            "delete_count": 0
        }
    
    def get_hot_files(self, db: Session, user_id: int, role: str) -> list:
        return []
    
    def get_stat_card(self, db: Session, user_id: int, role: str) -> dict:
        # 构建文件查询条件
        file_query = db.query(File).filter(File.is_deleted == 0)
        if role != "admin":
            file_query = file_query.filter(File.user_id == user_id)
        
        # 获取文件总数
        total_files = file_query.count()
        
        # 获取总大小
        total_size = db.query(func.sum(File.size)).filter(
            File.is_deleted == 0
        )
        if role != "admin":
            total_size = total_size.filter(File.user_id == user_id)
        total_size = total_size.scalar() or 0
        
        # 获取今日上传数量
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_uploads = db.query(File).filter(
            File.is_deleted == 0,
            File.create_time >= today_start
        )
        if role != "admin":
            today_uploads = today_uploads.filter(File.user_id == user_id)
        today_uploads = today_uploads.count()
        
        # 获取今日登录用户数
        today_logins = db.query(User).filter(
            User.last_login_time >= today_start
        ).count()
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "today_uploads": today_uploads,
            "today_logins": today_logins
        }


