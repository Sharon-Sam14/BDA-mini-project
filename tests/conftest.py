# tests/conftest.py
"""Shared pytest fixtures: one local SparkSession + a tiny CSV fixture dataset.

Fixture data is generated in-memory (24 events, 6 products, 6 inventory rows)
and written to CSV so tests exercise the same read path as production.
Runs offline, no HDFS required (Rules.md 9.4).
"""
import os
import sys
from pathlib import Path

# Environment fixes required for PySpark on this Windows machine:
# - HADOOP_HOME: winutils/hadoop.dll for Parquet writes (see README Part 1 2-3)
# - PYSPARK_PYTHON: the default `python3` resolves to the unspawnable
#   WindowsApps Store alias, which crashes every Python worker.
os.environ.setdefault("HADOOP_HOME", r"C:\hadoop")
os.environ.setdefault("PYSPARK_PYTHON", "python")
os.environ["PATH"] = r"C:\hadoop\bin" + os.pathsep + os.environ.get("PATH", "")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "spark"))

import pytest  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402

PRODUCTS = [
    ("PRD_00001", "Alpha Phone", "Electronics", 20000.0),
    ("PRD_00002", "Beta Shoes", "Footwear", 1500.0),
    ("PRD_00003", "Gamma Book", "Books", 400.0),
    ("PRD_00004", "Delta Mixer", "Home Appliances", 5000.0),
    ("PRD_00005", "Epsilon Ball", "Sports Equipment", 800.0),
    ("PRD_00006", "Zeta Cream", "Beauty", 600.0),
]

# (event_id, user_id, product_id, timestamp, event_type, city, state, lat, lon,
#  price, discount_percent, quantity)
EVENTS = [
    # Bengaluru - Alpha Phone dominates (high demand, low stock case)
    ("e01", "u1", "PRD_00001", "2026-09-01 10:00:00", "search",   "Bengaluru", "Karnataka", 12.9716, 77.5946, 20000.0, 0, 1),
    ("e02", "u2", "PRD_00001", "2026-09-01 11:00:00", "search",   "Bengaluru", "Karnataka", 12.9716, 77.5946, 20000.0, 0, 1),
    ("e03", "u3", "PRD_00001", "2026-09-01 12:00:00", "view",     "Bengaluru", "Karnataka", 12.9716, 77.5946, 20000.0, 0, 1),
    ("e04", "u3", "PRD_00001", "2026-09-01 13:00:00", "cart",     "Bengaluru", "Karnataka", 12.9716, 77.5946, 20000.0, 10, 1),
    ("e05", "u3", "PRD_00001", "2026-09-01 14:00:00", "purchase", "Bengaluru", "Karnataka", 12.9716, 77.5946, 18000.0, 10, 2),
    # Bengaluru - Gamma Book (low demand, high stock case)
    ("e06", "u4", "PRD_00003", "2026-09-02 09:00:00", "view",     "Bengaluru", "Karnataka", 12.9716, 77.5946, 400.0, 0, 1),
    ("e07", "u5", "PRD_00003", "2026-09-02 10:00:00", "purchase", "Bengaluru", "Karnataka", 12.9716, 77.5946, 400.0, 0, 1),
    # Mumbai - Beta Shoes (balanced)
    ("e08", "u6", "PRD_00002", "2026-09-03 08:00:00", "search",   "Mumbai", "Maharashtra", 19.076, 72.8777, 1500.0, 0, 1),
    ("e09", "u7", "PRD_00002", "2026-09-03 09:00:00", "cart",     "Mumbai", "Maharashtra", 19.076, 72.8777, 1500.0, 5, 1),
    ("e10", "u7", "PRD_00002", "2026-09-03 10:00:00", "purchase", "Mumbai", "Maharashtra", 19.076, 72.8777, 1425.0, 5, 1),
    ("e11", "u8", "PRD_00004", "2026-09-03 11:00:00", "purchase", "Mumbai", "Maharashtra", 19.076, 72.8777, 5000.0, 0, 1),
    ("e12", "u9", "PRD_00005", "2026-09-03 12:00:00", "search",   "Mumbai", "Maharashtra", 19.076, 72.8777, 800.0, 0, 1),
    # Delhi - purchases dominate (top category check)
    ("e13", "u10", "PRD_00004", "2026-09-04 15:00:00", "purchase", "Delhi", "Delhi", 28.7041, 77.1025, 5000.0, 0, 3),
    ("e14", "u11", "PRD_00004", "2026-09-04 16:00:00", "purchase", "Delhi", "Delhi", 28.7041, 77.1025, 4500.0, 10, 1),
    ("e15", "u12", "PRD_00006", "2026-09-04 17:00:00", "view",     "Delhi", "Delhi", 28.7041, 77.1025, 600.0, 0, 1),
    ("e16", "u12", "PRD_00006", "2026-09-04 18:00:00", "purchase", "Delhi", "Delhi", 28.7041, 77.1025, 600.0, 0, 1),
    # Invalid rows for cleaning tests
    ("e17", "u13", "PRD_00001", "2026-09-05 10:00:00", "purchase", "Delhi", "Delhi", 28.7041, 77.1025, -5.0, 0, 1),       # BAD_PRICE
    ("e18", "u14", "PRD_00001", "2026-09-05 11:00:00", "purchase", "Delhi", "Delhi", 28.7041, 77.1025, 100.0, 95, 1),     # BAD_DISCOUNT
    ("e19", "u15", "PRD_00001", "not-a-timestamp",      "view",     "Delhi", "Delhi", 28.7041, 77.1025, 100.0, 0, 1),     # BAD_TIMESTAMP
    ("e20", "u16", "PRD_99999", "2026-09-05 12:00:00", "view",     "Delhi", "Delhi", 28.7041, 77.1025, 100.0, 0, 1),     # BROKEN_FK_PRODUCT
    ("e21", "u17", "PRD_00001", "2026-09-05 13:00:00", "like",     "Delhi", "Delhi", 28.7041, 77.1025, 100.0, 0, 1),      # BAD_EVENT_TYPE
    ("e22", "u18", "PRD_00001", "2026-09-05 14:00:00", "view",     "Delhi", "Delhi", 45.0, 77.1025, 100.0, 0, 1),         # BAD_COORDINATES
    ("e01", "u1", "PRD_00001", "2026-09-01 10:00:00", "search",   "Bengaluru", "Karnataka", 12.9716, 77.5946, 20000.0, 0, 1),  # duplicate event_id
]

INVENTORY = [
    ("PRD_00001", "Bengaluru", 5, "2026-09-25"),    # high demand + low stock
    ("PRD_00003", "Bengaluru", 400, "2026-09-25"),  # low demand + high stock
    ("PRD_00002", "Mumbai", 30, "2026-09-25"),      # balanced
    ("PRD_00004", "Mumbai", 200, "2026-09-25"),
    ("PRD_00005", "Mumbai", 150, "2026-09-25"),
    ("PRD_00004", "Delhi", 50, "2026-09-25"),
    ("PRD_00006", "Delhi", 100, "2026-09-25"),
]

EVENT_COLUMNS = ["event_id", "user_id", "product_id", "timestamp", "event_type",
                 "city", "state", "latitude", "longitude", "price",
                 "discount_percent", "quantity"]
PRODUCT_COLUMNS = ["product_id", "product_name", "category", "base_price"]
INVENTORY_COLUMNS = ["product_id", "city", "available_stock", "date"]


@pytest.fixture(scope="session")
def spark():
    session = (SparkSession.builder
               .master("local[2]")
               .appName("BDA-Mini-Tests")
               .config("spark.ui.enabled", "false")
               .config("spark.sql.shuffle.partitions", "2")
               .config("spark.driver.memory", "1g")
               .getOrCreate())
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


@pytest.fixture(scope="session")
def fixture_paths(tmp_path_factory):
    """Write the tiny fixture dataset as CSVs and return storage paths dict."""
    import csv
    base = tmp_path_factory.mktemp("fixture")
    for entity, cols, rows in (
        ("events", EVENT_COLUMNS, EVENTS),
        ("products", PRODUCT_COLUMNS, PRODUCTS),
        ("inventory", INVENTORY_COLUMNS, INVENTORY),
    ):
        entity_dir = base / "raw" / entity
        entity_dir.mkdir(parents=True, exist_ok=True)
        with open(entity_dir / f"{entity}.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(cols)
            writer.writerows(rows)
    (base / "processed").mkdir(exist_ok=True)
    return {
        "mode": "local",
        "raw_base": str(base / "raw").replace("\\", "/"),
        "processed_base": str(base / "processed").replace("\\", "/"),
    }
