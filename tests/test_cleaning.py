# tests/test_cleaning.py
"""Tests for spark/preprocessing/clean_events.py (Member 2 data cleaning)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spark"))

from pyspark.sql import functions as F

from preprocessing.clean_events import build_products, clean_events
from utils.io_helpers import read_raw_csv


def test_cleaning_removes_all_documented_bad_rows(spark, fixture_paths):
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, quarantine, rejected_counts, dup_count = clean_events(raw, products)

    # 23 input rows - 1 duplicate - 6 invalid = 16 clean rows
    assert dup_count == 1
    assert clean.count() == 16
    assert quarantine.count() == 6

    reasons = {r["quarantine_reason"]: r["count"]
               for r in rejected_counts.collect()}
    assert reasons == {
        "BAD_PRICE": 1,
        "BAD_DISCOUNT": 1,
        "BAD_TIMESTAMP": 1,
        "BROKEN_FK_PRODUCT": 1,
        "BAD_EVENT_TYPE": 1,
        "BAD_COORDINATES": 1,
    }


def test_clean_rows_have_correct_types(spark, fixture_paths):
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, *_ = clean_events(raw, products)

    dtypes = dict(clean.dtypes)
    assert dtypes["timestamp"] == "timestamp"
    assert dtypes["price"] == "double"
    assert dtypes["latitude"] == "double"
    assert dtypes["longitude"] == "double"
    assert dtypes["discount_percent"] == "int"
    assert dtypes["quantity"] == "int"

    # No nulls survive in critical columns
    for col in ("event_id", "user_id", "product_id", "timestamp",
                "city", "price", "quantity"):
        assert clean.filter(F.col(col).isNull()).count() == 0


def test_cleaning_deduplicates_on_event_id(spark, fixture_paths):
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, *_ = clean_events(raw, products)
    assert clean.select("event_id").distinct().count() == clean.count()


def test_quarantine_is_preserved_not_deleted(spark, fixture_paths):
    """Quarantined rows must be returned (auditable), not dropped silently."""
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, quarantine, *_ = clean_events(raw, products)
    assert clean.count() + quarantine.count() + 1 == raw.count()  # +1 dedup
