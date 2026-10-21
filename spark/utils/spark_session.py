# spark/utils/spark_session.py
import os
import sys
from pyspark.sql import SparkSession

def build_spark_session(app_name="GeoSpatialAnalyticsEngine"):
    """
    Constructs an optimized, reusable SparkSession factory module.
    Enforces architectural criteria regarding resource allocation and configuration controls.
    """
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]") \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
            .getOrCreate()
            
        # Suppress non-blocking Windows environment log warnings
        spark.sparkContext.setLogLevel("ERROR")
        return spark
        
    except Exception as e:
        print(f"❌ CRITICAL INITIALIZATION ERROR: Failed to instantiate Spark driver session context. Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Test block to verify path safety on Windows local filesystems
    print("Testing Spark Session builder factory configuration constraints...")
    session = build_spark_session("InfrastructureSmokeTest")
    print(f"✅ Success: Connected to Spark Cluster context. App Name: {session.sparkContext.appName}")
    session.stop()
