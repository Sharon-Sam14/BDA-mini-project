# spark/processing/process_mismatch.py
import os
import sys

# 1. Force Python to recognize the root workspace directory path for internal imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, round as _round

def main():
    # 2. Initialize optimized local PySpark cluster engine instance
    spark = SparkSession.builder \
        .appName("Ecommerce-Supply-Demand-Mismatch") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    print("\n[INFO] PySpark Session Initialized for Module 3 Mismatch Detection...")

    # 3. Local File System absolute URL path maps
    demand_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/processed/demand_scores"
    inventory_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/inventory/inventory.csv"
    output_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/processed/supply_demand"

    print("[INFO] Loading pre-calculated demand scores and raw warehouse snapshot arrays...")
    demand_df = spark.read.parquet(demand_path)
    # Note: process_demand_scores drops product_id during column pruning. 
    # For a direct relational join, we reconstruct or map using product_name / city matching logic
    # or leverage products catalog alignment. Let's load inventory and read city metrics.
    inventory_df = spark.read.csv(inventory_path, header=True, inferSchema=True)

    # 4. Read the product catalog to map item names back to IDs for clean joining
    products_path = "file:///D:/PROJECTS/BDA-mini-project-main/data/raw/products/products.csv"
    products_df = spark.read.csv(products_path, header=True, inferSchema=True)

    # Re-attach product_id to demand frame to ensure exact relational consistency
    demand_with_id = demand_df.join(products_df, "product_name", "inner")

    # 5. Execute distributed inner join on unique keys: (product_id, city)
    print("[INFO] Performing distributed relational join across demand vectors and inventory grids...")
    joined_df = demand_with_id.join(
        inventory_df,
        (demand_with_id.product_id == inventory_df.product_id) & (demand_with_id.city == inventory_df.city),
        "inner"
    )

    # 6. Apply core mathematical calculations for Stock-to-Demand Ratio (SDR)
    # Introduce K_scale scaling modifier coefficient (e.g., 500) to balance available units
    print("[INFO] Categorizing supply mismatch indexes and capital lockup vulnerability metrics...")
    mismatch_df = joined_df.withColumn(
        "sdr",
        _round(col("available_stock") / ((col("demand_score") * 500) + 1), 4)
    ).withColumn(
        "status",
        when(col("sdr") < 0.5, "CRITICAL_SHORTAGE")
        .when(col("sdr") > 2.0, "EXCESS_INVENTORY")
        .otherwise("BALANCED")
    )

    # Prune and filter target output column nodes
    final_mismatch_df = mismatch_df.select(
        demand_with_id.state,
        demand_with_id.city,
        "product_name",
        "available_stock",
        "demand_score",
        "sdr",
        "status"
    ).orderBy("sdr")

    print("\n--- SAMPLE SUPPLY-DEMAND MISMATCH MATRIX ---")
    final_mismatch_df.show(10, truncate=False)

    # 7. Materialize final dataset table locally in partitioned snappy parquet files
    print(f"[INFO] Saving mismatch metrics to local path: {output_path}")
    final_mismatch_df.write.mode("overwrite").parquet(output_path)
    
    print("[SUCCESS] Module 3 Ingestion Pipeline Processing Completed Cleanly!\n")
    spark.stop()

if __name__ == "__main__":
    main()
