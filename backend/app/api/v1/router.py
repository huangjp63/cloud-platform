from fastapi import APIRouter
from app.api.v1 import user, folder, file, recycle, analysis, monitor, admin

api_router = APIRouter()

api_router.include_router(user.router, prefix="/user", tags=["用户模块"])
api_router.include_router(folder.router, prefix="/folder", tags=["文件夹模块"])
api_router.include_router(file.router, prefix="/file", tags=["文件模块"])
api_router.include_router(recycle.router, prefix="/recycle", tags=["回收站模块"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["大数据分析模块"])
api_router.include_router(monitor.router, prefix="/monitor", tags=["系统监控模块"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员模块"])
