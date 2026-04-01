from sqlalchemy.orm import Session


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
        return {
            "total_files": 0,
            "total_size": 0,
            "today_uploads": 0,
            "today_logins": 0
        }
