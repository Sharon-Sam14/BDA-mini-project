# tests/test_data_loading.py
"""Member 1/2 boundary tests: schema, types, required fields, fixture integrity."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spark"))

from pyspark.sql import functions as F

from utils.io_helpers import read_raw_csv
from utils.schemas import EVENTS_SCHEMA, INVENTORY_SCHEMA, PRODUCTS_SCHEMA

REQUIRED_EVENT_FIELDS = [
    "event_id", "user_id", "product_id", "timestamp", "event_type",
    "city", "state", "latitude", "longitude", "price",
    "discount_percent", "quantity",
]


def test_required_event_fields_present():
    """The dataset must support user id, product id, event type, timestamp,
    city/region, lat/lon, price, discount, quantity (task requirement)."""
    schema_fields = [f.name for f in EVENTS_SCHEMA.fields]
    assert schema_fields == REQUIRED_EVENT_FIELDS


def test_inventory_schema_has_supply_fields():
    names = [f.name for f in INVENTORY_SCHEMA.fields]
    assert names == ["product_id", "city", "available_stock", "date"]
    assert INVENTORY_SCHEMA["available_stock"].dataType.simpleString() == "int"


def test_product_schema_matches_prd():
    names = [f.name for f in PRODUCTS_SCHEMA.fields]
    assert names == ["product_id", "product_name", "category", "base_price"]


def test_raw_events_csv_loads(spark, fixture_paths):
    df = read_raw_csv(spark, "events", fixture_paths)
    assert df.count() == 23  # 22 unique + 1 duplicate row for cleaning test
    assert set(df.columns) == set(REQUIRED_EVENT_FIELDS)


def test_inventory_and_products_load(spark, fixture_paths):
    inv = read_raw_csv(spark, "inventory", fixture_paths)
    prod = read_raw_csv(spark, "products", fixture_paths)
    assert inv.count() == 7
    assert prod.count() == 6


def test_fixture_event_types_and_geo_are_valid(spark, fixture_paths):
    """Fixture rows outside the validation bounds must exist (for cleaning
    tests), valid rows must be inside them."""
    df = read_raw_csv(spark, "events", fixture_paths)
    # All 4 documented funnel types present
    types = {r[0] for r in df.select("event_type").distinct().collect()}
    assert {"search", "view", "cart", "purchase"} <= types
    # Indian coordinate bounds (8-38N, 68-98E) hold for >= 16 valid rows
    valid_geo = df.filter((F.col("latitude").cast("double").between(8, 38))
                          & (F.col("longitude").cast("double").between(68, 98)))
    assert valid_geo.count() >= 16
