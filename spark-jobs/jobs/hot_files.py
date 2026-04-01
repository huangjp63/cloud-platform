from pyspark.sql.functions import col, count, desc
from config.spark_config import create_spark_session


def run_hot_files_analysis(user_id=None, limit=10):
    spark = create_spark_session("HotFilesAnalysis")
    
    try:
        df = spark.read \
            .format("org.elasticsearch.spark.sql") \
            .option("es.nodes", "elasticsearch") \
            .option("es.port", "9200") \
            .option("es.resource", "file_access_logs") \
            .load()
        
        filtered_df = df.filter(col("action") == "download")
        
        if user_id:
            filtered_df = filtered_df.filter(col("user_id") == user_id)
        
        hot_files = filtered_df.groupBy("file_id", "file_name") \
            .agg(count("*").alias("access_count")) \
            .orderBy(desc("access_count")) \
            .limit(limit) \
            .collect()
        
        result = [
            {
                "file_id": row["file_id"],
                "file_name": row["file_name"],
                "access_count": row["access_count"]
            }
            for row in hot_files
        ]
        
        return result
        
    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_hot_files_analysis()
    print(result)
