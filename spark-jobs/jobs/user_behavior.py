from pyspark.sql.functions import col, count, desc
from config.spark_config import create_spark_session, get_date_range


def run_user_behavior_analysis(range_type="day", user_id=None):
    spark = create_spark_session("UserBehaviorAnalysis")
    
    try:
        df = spark.read \
            .format("org.elasticsearch.spark.sql") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.resource", "user_logs") \
            .load()
        
        start_date, end_date = get_date_range(range_type)
        
        filtered_df = df.filter(
            (col("timestamp") >= start_date) & 
            (col("timestamp") <= end_date)
        )
        
        if user_id:
            filtered_df = filtered_df.filter(col("user_id") == user_id)
        
        login_count = filtered_df.filter(col("action") == "login").count()
        upload_count = filtered_df.filter(col("action") == "upload").count()
        download_count = filtered_df.filter(col("action") == "download").count()
        delete_count = filtered_df.filter(col("action") == "delete").count()
        
        result = {
            "login_count": login_count,
            "upload_count": upload_count,
            "download_count": download_count,
            "delete_count": delete_count,
            "range_type": range_type
        }
        
        return result
        
    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_user_behavior_analysis("day")
    print(result)
