from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.clean_recycle import clean_recycle_task
from app.tasks.spark_analysis import run_spark_analysis

scheduler = AsyncIOScheduler()


def setup_scheduler():
    scheduler.add_job(clean_recycle_task, "cron", hour=3, minute=0, id="clean_recycle")
    scheduler.add_job(run_spark_analysis, "cron", hour=2, minute=0, id="spark_analysis")
    scheduler.start()
