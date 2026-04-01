from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, desc
from datetime import datetime, timedelta


def create_spark_session(app_name="CloudPlatformAnalysis"):
    return SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.es.nodes", "elasticsearch") \
        .config("spark.es.port", "9200") \
        .getOrCreate()


def get_date_range(range_type="day"):
    now = datetime.now()
    if range_type == "day":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif range_type == "week":
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start, now
