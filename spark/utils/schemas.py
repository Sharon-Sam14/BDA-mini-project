# spark/utils/schemas.py
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, DateType

# 1. Clickstream & Transactions Log Schema (events)
EVENTS_SCHEMA = StructType([
    StructField("event_id", StringType(), False),
    StructField("user_id", StringType(), False),
    StructField("product_id", StringType(), False),
    StructField("timestamp", TimestampType(), True),
    StructField("event_type", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("price", DoubleType(), True),
    StructField("discount_percent", IntegerType(), True),
    StructField("quantity", IntegerType(), True)
])

# 2. Product Master Catalog Schema (products)
PRODUCTS_SCHEMA = StructType([
    StructField("product_id", StringType(), False),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("base_price", DoubleType(), True)
])

# 3. Warehouse Inventory Snapshot Schema (inventory)
INVENTORY_SCHEMA = StructType([
    StructField("product_id", StringType(), False),
    StructField("city", StringType(), False),
    StructField("available_stock", IntegerType(), True),
    StructField("date", DateType(), True)
])

if __name__ == "__main__":
    print("🚀 Verifying structural blueprint definitions...")
    print(f"Events Fields: {len(EVENTS_SCHEMA.fields)}")
    print(f"Products Fields: {len(PRODUCTS_SCHEMA.fields)}")
    print(f"Inventory Fields: {len(INVENTORY_SCHEMA.fields)}")
    print("✅ StructType master schemas successfully loaded and ready for ingestion.")
