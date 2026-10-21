# spark/processing/process_demand_scores.py
import os
import sys

# 1. Force Python to recognize the root workspace directory path for internal imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, sum as _sum, min as _min, max as _max, round as _round

def main():
    # 2. Boot optimized local PySpark cluster engine instance
    spark = SparkSession.builder \
        .appName("Ecommerce-Weighted-Demand-Scoring") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    print("\n[INFO] PySpark Session Initialized for Module 2 Scoring...")

    # 3. Local File System absolute URL path maps
    events_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/events/events.csv"
    products_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/products/products.csv"
    output_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/processed/demand_scores"

    print("[INFO] Loading transaction data log layers...")
    events_df = spark.read.csv(events_path, header=True, inferSchema=True)
    products_df = spark.read.csv(products_path, header=True, inferSchema=True)

    # 4. Pivot and aggregate funnel action counts per product and location hub
    print("[INFO] Computing aggregated funnel action frequency vectors...")
    pivoted_df = events_df.groupBy("city", "state", "product_id") \
        .pivot("event_type", ["search", "view", "cart", "purchase"]) \
        .count() \
        .na.fill(0) # Standardize missing metrics to 0 bounds

    # 5. Apply min-max normalization metrics to equalize action values across partitions
    # To protect against division-by-zero crashes, introduce a minor epsilon buffer flag (+ 0.001)
    stats_df = pivoted_df.agg(
        _max("search").alias("max_s"), _min("search").alias("min_s"),
        _max("view").alias("max_v"), _min("view").alias("min_v"),
        _max("cart").alias("max_c"), _min("cart").alias("min_c"),
        _max("purchase").alias("max_p"), _min("purchase").alias("min_p")
    ).collect()[0]

    # 6. Mathematically apply your PRD-mandated weighted demand formula rules matrix
    print("[INFO] Orchestrating mathematical composite weighting calculations...")
    scored_df = pivoted_df.withColumn(
        "demand_score",
        _round(
            0.15 * ((col("search") - stats_df["min_s"]) / (stats_df["max_s"] - stats_df["min_s"] + 0.001)) +
            0.20 * ((col("view") - stats_df["min_v"]) / (stats_df["max_v"] - stats_df["min_v"] + 0.001)) +
            0.30 * ((col("cart") - stats_df["min_c"]) / (stats_df["max_c"] - stats_df["min_c"] + 0.001)) +
            0.35 * ((col("purchase") - stats_df["min_p"]) / (stats_df["max_p"] - stats_df["min_p"] + 0.001)),
            4
        )
    )

    # Join catalog dimension details to bind readable item labels
    final_demand_df = scored_df.join(products_df, "product_id", "inner") \
        .select("state", "city", "product_name", "category", "demand_score") \
        .orderBy(col("demand_score").desc())

    print("\n--- SAMPLE COMPOSITE DEMAND SCORING MATRIX ---")
    final_demand_df.show(10, truncate=False)

    # 7. Materialize final dataset table locally in partitioned snappy parquet files
    print(f"[INFO] Saving processed demand analytics to local disk path: {output_path}")
    final_demand_df.write.mode("overwrite").parquet(output_path)
    
    print("[SUCCESS] Module 2 Aggregations Completed Successfully!\n")
    spark.stop()

if __name__ == "__main__":
    main()
