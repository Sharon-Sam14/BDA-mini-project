# spark/processing/process_regional_trends.py
import os
import sys

# 1. Force Python to recognize the root workspace directory path for internal imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, round, desc

def main():
    # 2. Initialize PySpark Session locally with optimized system partition sizes
    spark = SparkSession.builder \
        .appName("Ecommerce-Regional-Trends-Analytics") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    print("\n[INFO] PySpark Session Initialized Successfully.")

    # 3. Local File System absolute URL path maps (Windows Safe Scheme)
    events_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/events/events.csv"
    products_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/products/products.csv"
    inventory_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/inventory/inventory.csv"
    output_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/processed/regional_trends"

    print("[INFO] Reading raw datasets from local disk storage layers...")
    events_df = spark.read.csv(events_path, header=True, inferSchema=True)
    products_df = spark.read.csv(products_path, header=True, inferSchema=True)

    # 4. Data Cleaning & Transformations (Filter conversions and inner join dimension tables)
    purchases_df = events_df.filter(col("event_type") == "purchase")
    
    enriched_purchases = purchases_df.join(
        products_df, 
        purchases_df.product_id == products_df.product_id, 
        "inner"
    )

    # 5. Distributed Aggregations Matrix (Grouping by state and category metrics)
    # This variable matches the reference in the write layer below exactly
    regional_trends = enriched_purchases.groupBy("state", "category") \
        .agg(
            count("event_id").alias("total_orders"),
            round(_sum("price"), 2).alias("total_revenue")
        ) \
        .orderBy("state", desc("total_revenue"))

    print("\n--- SAMPLE REGIONAL TRENDS SUMMARY ---")
    regional_trends.show(10, truncate=False)

    # 6. Write Aggregated Vector Data Back to Local Disk in Columnar Parquet format
    print(f"[INFO] Writing processed Parquet results to local path: {output_path}")
    regional_trends.write \
        .mode("overwrite") \
        .parquet(output_path)

    print("[SUCCESS] Phase 7 Processing Completed Successfully!\n")
    spark.stop()

if __name__ == "__main__":
    main()
