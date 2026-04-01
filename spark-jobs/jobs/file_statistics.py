from pyspark.sql.functions import col, count, sum, desc
from config.spark_config import create_spark_session, get_date_range


def run_file_statistics(range_type="day"):
    spark = create_spark_session("FileStatistics")
    
    try:
        df = spark.read \
            .format("org.elasticsearch.spark.sql") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.resource", "file_logs") \
            .load()
        
        start_date, end_date = get_date_range(range_type)
        
        filtered_df = df.filter(
            (col("timestamp") >= start_date) & 
            (col("timestamp") <= end_date)
        )
        
        upload_count = filtered_df.filter(col("action") == "upload").count()
        
        total_size = filtered_df.filter(col("action") == "upload") \
            .agg(sum("file_size").alias("total_size")) \
            .collect()[0]["total_size"] or 0
        
        type_distribution = filtered_df.filter(col("action") == "upload") \
            .groupBy("file_type") \
            .agg(count("*").alias("count")) \
            .collect()
        
        result = {
            "upload_count": upload_count,
            "total_size": total_size,
            "type_distribution": {row["file_type"]: row["count"] for row in type_distribution},
            "range_type": range_type
        }
        
        return result
        
    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_file_statistics("day")
    print(result)
