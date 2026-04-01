from app.utils.log_utils import logger
from app.database import SessionLocal
from app.services.recycle_service import RecycleService


async def clean_recycle_task():
    logger.info("开始执行回收站清理任务...")
    db = SessionLocal()
    try:
        recycle_service = RecycleService()
        count = recycle_service.clean_expired_items(db)
        logger.info(f"回收站清理完成，共清理 {count} 个过期项目")
    except Exception as e:
        logger.error(f"回收站清理任务执行失败: {e}")
    finally:
        db.close()
