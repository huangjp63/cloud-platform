from app.services.user_service import UserService
from app.services.file_service import FileService
from app.services.folder_service import FolderService
from app.services.recycle_service import RecycleService
from app.services.analysis_service import AnalysisService
from app.services.monitor_service import MonitorService
from app.services.admin_service import AdminService

user_service = UserService()
file_service = FileService()
folder_service = FolderService()
recycle_service = RecycleService()
analysis_service = AnalysisService()
monitor_service = MonitorService()
admin_service = AdminService()

__all__ = [
    "user_service", "file_service", "folder_service",
    "recycle_service", "analysis_service", "monitor_service", "admin_service"
]
