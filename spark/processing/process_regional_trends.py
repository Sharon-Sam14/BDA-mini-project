import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, round, desc

def main():
    # 1. Initialize PySpark Session with HDFS Support
    spark = SparkSession.builder \
        .appName("Ecommerce-Regional-Trends-Analytics") \
        .master("local[*]") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    print("\n[INFO] PySpark Session Initialized Successfully.")

    # 2. HDFS Input and Output Paths
    hdfs_base_url = "hdfs://localhost:9000"
    events_path = f"{hdfs_base_url}/ecommerce/raw/events/events.csv"
    products_path = f"{hdfs_base_url}/ecommerce/raw/products/products.csv"
    inventory_path = f"{hdfs_base_url}/ecommerce/raw/inventory/inventory.csv"
    output_path = f"{hdfs_base_url}/ecommerce/processed/regional_trends"

    # 3. Read Raw CSV Datasets from HDFS
    print("[INFO] Reading raw datasets from HDFS...")
    events_df = spark.read.csv(events_path, header=True, inferSchema=True)
    products_df = spark.read.csv(products_path, header=True, inferSchema=True)
    inventory_df = spark.read.csv(inventory_path, header=True, inferSchema=True)

    # 4. Data Cleaning & Transformations
    # Filter purchase events and join with product catalog to compute revenue
    purchases_df = events_df.filter(col("event_type") == "purchase")
    
    enriched_purchases = purchases_df.join(
        products_df, 
        purchases_df.product_id == products_df.product_id, 
        "inner"
    )

    # 5. Regional Aggregations (Grouping by 'state' and 'category')
    regional_trends = enriched_purchases.groupBy("state", "category") \
        .agg(
            count("event_id").alias("total_orders"),
            round(_sum("price"), 2).alias("total_revenue")
        ) \
        .orderBy("state", desc("total_revenue"))

    print("\n--- SAMPLE REGIONAL TRENDS SUMMARY ---")
    regional_trends.show(10, truncate=False)

    # 6. Write Aggregated Results Back to HDFS in Parquet Format
    print(f"[INFO] Writing processed Parquet results to HDFS: {output_path}")
    regional_trends.write \
        .mode("overwrite") \
        .parquet(output_path)

    print("[SUCCESS] Phase 7 Processing Completed Successfully!\n")
    spark.stop()

if __name__ == "__main__":
    main()