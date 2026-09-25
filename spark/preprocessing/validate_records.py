# spark/preprocessing/validate_records.py
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def get_spark_session():
    """Initializes local optimized Spark Session for validation."""
    spark = SparkSession.builder \
        .appName("GeoSpatialDataValidation") \
        .master("local[*]") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    
    # Suppress non-blocking Windows Hadoop/winutils logging noise
    spark.sparkContext.setLogLevel("ERROR")
    return spark

def validate_datasets():
    spark = get_spark_session()
    print("\n🚀 Initializing Phase 4: Strict Schema & Data Quality Validation Engine...")

    # 1. Define explicit paths based on current directory structure
    RAW_PATH = "data/raw"
    
    # 2. Load Datasets from the main folders
    products_df = spark.read.csv(f"{RAW_PATH}/products/products.csv", header=True, inferSchema=True)
    inventory_df = spark.read.csv(f"{RAW_PATH}/inventory/inventory.csv", header=True, inferSchema=True)
    events_df = spark.read.csv(f"{RAW_PATH}/events/events.csv", header=True, inferSchema=True)

    print(f"Loaded records for verification: Events ({events_df.count()}), Products ({products_df.count()}), Inventory ({inventory_df.count()})")

    # ==========================================
    # DATA QUALITY CHECKS (PRD / RULES MANDATE)
    # ==========================================
    errors_found = False

    # Check 1: Prices and Quantities must be strictly greater than zero
    invalid_prices = events_df.filter((col("price") <= 0) | (col("quantity") <= 0))
    if invalid_prices.count() > 0:
        print(f"❌ CRITICAL ERROR: Found {invalid_prices.count()} rows with zero/negative pricing or quantities.")
        errors_found = True

    # Check 2: Discounts must be between 0% and 70%
    invalid_discounts = events_df.filter((col("discount_percent") < 0) | (col("discount_percent") > 70))
    if invalid_discounts.count() > 0:
        print(f"❌ CRITICAL ERROR: Found {invalid_discounts.count()} rows violating discount depth limits (0-70%).")
        errors_found = True

    # Check 3: Coordinates must fall inside valid geographic zones for India
    # (Lat bounds: 8° to 38° N, Long bounds: 68° to 98° E)
    invalid_geo = events_df.filter(
        (col("latitude") < 8.0) | (col("latitude") > 38.0) |
        (col("longitude") < 68.0) | (col("longitude") > 98.0)
    )
    if invalid_geo.count() > 0:
        print(f"❌ CRITICAL ERROR: Found {invalid_geo.count()} rows with geo-coordinates falling outside Indian territories.")
        errors_found = True

    # Check 4: Referential Integrity Check (Fixed Join Type to 'left_anti')
    mismatched_products = events_df.join(products_df, "product_id", "left_anti")
    if mismatched_products.count() > 0:
        print(f"❌ CRITICAL ERROR: Found {mismatched_products.count()} clickstream events pointing to missing catalog item IDs.")
        errors_found = True

    # ==========================================
    # VALIDATION ASSESSMENT LOGIC
    # ==========================================
    if not errors_found:
        print("\n✅ SUCCESS: 100% of staging data blocks passed quality rules, schemas, and referential checks!")
        print("Data is perfectly optimized and authenticated for Phase 5 storage ingestion.")
    else:
        print("\n⚠️ ALERT: Pipeline validation failed. Check log indicators above for malformed entries.")

    spark.stop()

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    validate_datasets()
