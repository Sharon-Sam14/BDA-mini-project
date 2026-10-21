# tests/test_regional_trends.py
"""Tests for regional trend aggregation (Module 1, DataFrame API + Spark SQL)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spark"))

from pyspark.sql import functions as F

from analytics.regional_trends import (location_metrics, top_categories_by_state,
                                       top_products_by_location)
from analytics.spark_sql_queries import QUERIES
from preprocessing.clean_events import build_products, clean_events
from utils.io_helpers import read_raw_csv


def _cleaned(spark, fixture_paths):
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, *_ = clean_events(raw, products)
    return clean, products


def test_top_products_by_city_per_event_type(spark, fixture_paths):
    """Bengaluru searches: only PRD_00001 has search events (2 of them)."""
    events, products = _cleaned(spark, fixture_paths)
    top = top_products_by_location(events, products, "city", top_n=3)
    blr_search = (top.filter((F.col("city") == "Bengaluru")
                             & (F.col("event_type") == "search"))
                  .collect())
    assert len(blr_search) == 1
    assert blr_search[0]["product_id"] == "PRD_00001"
    assert blr_search[0]["event_count"] == 2
    assert blr_search[0]["rank"] == 1


def test_top_products_respects_top_n(spark, fixture_paths):
    events, products = _cleaned(spark, fixture_paths)
    top = top_products_by_location(events, products, "city", top_n=1)
    # every (city, event_type) partition keeps only rank 1
    assert all(r["rank"] == 1 for r in top.collect())


def test_top_categories_by_state_gmv(spark, fixture_paths):
    """Delhi Home Appliances GMV = 5000*3 + 4500*1 = 19500 (hand-computed)."""
    events, products = _cleaned(spark, fixture_paths)
    cats = top_categories_by_state(events, products, top_n=5)
    delhi = {r["category"]: r for r in
             cats.filter(F.col("state") == "Delhi").collect()}
    assert "Home Appliances" in delhi
    ha = delhi["Home Appliances"]
    assert ha["rank"] == 1
    assert abs(ha["gmv"] - 19500.0) < 0.01
    assert ha["purchase_orders"] == 2  # e13 + e14
    assert ha["units_sold"] == 4       # 3 + 1


def test_location_metrics_totals(spark, fixture_paths):
    """Bengaluru: 7 clean events (e01-e07); revenue = 18000*2 + 400*1 = 36400."""
    events, _ = _cleaned(spark, fixture_paths)
    metrics = {r["city"]: r for r in location_metrics(events).collect()}
    blr = metrics["Bengaluru"]
    assert blr["total_events"] == 7
    assert blr["latitude"] == 12.9716
    assert abs(blr["total_revenue"] - 36400.0) < 0.01
    # fixture only uses 3 of the 8 documented Indian metros
    assert len(metrics) == 3


def test_spark_sql_agrees_with_dataframe_api(spark, fixture_paths):
    """The same top-city-searches result must come out of SQL and DataFrame API."""
    events, products = _cleaned(spark, fixture_paths)
    events.createOrReplaceTempView("events")
    products.createOrReplaceTempView("products")

    sql_top = spark.sql(QUERIES["top_products_city_sql"].format(top_n=3))
    api_top = top_products_by_location(events, products, "city", top_n=3)

    sql_rows = {(r["city"], r["event_type"], r["product_id"], r["event_count"])
                for r in sql_top.collect()}
    api_rows = {(r["city"], r["event_type"], r["product_id"], r["event_count"])
                for r in api_top.collect()}
    assert sql_rows == api_rows
    assert len(sql_rows) > 0


def test_spark_sql_event_mix_counts(spark, fixture_paths):
    events, products = _cleaned(spark, fixture_paths)
    events.createOrReplaceTempView("events")
    products.createOrReplaceTempView("products")
    mix = {r["city"]: r for r in
           spark.sql(QUERIES["event_mix_by_city_sql"]).collect()}
    assert mix["Bengaluru"]["searches"] == 2
    assert mix["Bengaluru"]["purchases"] == 2
    assert mix["Bengaluru"]["total_events"] == 7
    # funnel columns are consistent: parts sum to total
    for r in mix.values():
        assert (r["searches"] + r["views"] + r["carts"] + r["purchases"]
                == r["total_events"])
