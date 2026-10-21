# spark/analytics/regional_trends.py
"""Module 1 (Phase 7): Regional & geo-spatial trend detection in PySpark.

Consumes Member 1's cleaned events (written by
spark/preprocessing/clean_events.py) + the product dimension.

Outputs (Parquet, Snappy) under <processed_base>/regional_trends/:
- top_products_city      : top-N products per city, per event_type (FR-05)
- top_products_state     : top-N products per state, per event_type (FR-05)
- top_categories_state   : top categories per state by volume & GMV (FR-06)
- location_metrics       : lat/lon + event counts + revenue per city (FR-07)

All heavy lifting is distributed (groupBy + window + broadcast join);
no collect()/toPandas() on event-level data (Rules.md 4.2).
"""
from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

_SPARK_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_SPARK_ROOT), str(_SPARK_ROOT.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils.io_helpers import get_storage_paths, load_pipeline_config, read_processed, write_parquet  # noqa: E402
from utils.spark_session import build_spark_session  # noqa: E402


def load_cleaned_events(spark: SparkSession, paths: dict) -> DataFrame:
    """Read cleaned events written by Member 2's cleaning stage."""
    return read_processed(spark, "cleaned/events", paths)


def load_products(spark: SparkSession, paths: dict) -> DataFrame:
    """Read the product dimension directly from the Member 1 raw zone."""
    from utils.io_helpers import read_raw_csv
    return (read_raw_csv(spark, "products", paths)
            .withColumn("product_id", F.trim(F.col("product_id")))
            .withColumn("base_price", F.col("base_price").cast("double")))


def top_products_by_location(events: DataFrame, products: DataFrame,
                             location_col: str, top_n: int) -> DataFrame:
    """Top-N products per location per event_type using dense_rank windows (FR-05)."""
    enriched = events.join(F.broadcast(products), "product_id", "left")
    counts = (enriched.groupBy(location_col, "product_id", "product_name", "event_type")
              .agg(F.count("*").alias("event_count")))
    window = (Window.partitionBy(location_col, "event_type")
              .orderBy(F.desc("event_count")))
    return (counts.withColumn("rank", F.dense_rank().over(window))
            .filter(F.col("rank") <= top_n)
            .select(location_col, "event_type", "product_id", "product_name",
                    "event_count", "rank"))


def top_categories_by_state(events: DataFrame, products: DataFrame,
                            top_n: int) -> DataFrame:
    """Top categories per state by purchase volume and GMV (FR-06).

    GMV = sum(price * quantity) over purchase events only.
    """
    purchases = events.filter(F.col("event_type") == "purchase")
    enriched = purchases.join(F.broadcast(products), "product_id", "left")
    agg = (enriched.groupBy("state", "category")
           .agg(F.count("*").alias("purchase_orders"),
                F.sum(F.col("price") * F.col("quantity")).alias("gmv"),
                F.sum("quantity").alias("units_sold")))
    window = Window.partitionBy("state").orderBy(F.desc("gmv"))
    return (agg.withColumn("rank", F.dense_rank().over(window))
            .filter(F.col("rank") <= top_n)
            .select("state", "category", "purchase_orders", "units_sold",
                    F.round("gmv", 2).alias("gmv"), "rank"))


def location_metrics(events: DataFrame) -> DataFrame:
    """Aggregated geo metrics per city for map rendering (FR-07)."""
    return (events.groupBy("city", "state", "latitude", "longitude")
            .agg(F.count("*").alias("total_events"),
                 F.countDistinct("user_id").alias("unique_users"),
                 F.sum(F.when(F.col("event_type") == "purchase",
                              F.col("price") * F.col("quantity"))
                        .otherwise(0)).alias("total_revenue"))
            .orderBy(F.desc("total_events")))


def run(events: DataFrame, products: DataFrame, top_n: int, paths: dict) -> None:
    """Compute and persist all Module 1 outputs."""
    print(f"[M1] Top-{top_n} products per city/state, categories per state, geo metrics...")
    write_parquet(top_products_by_location(events, products, "city", top_n),
                  "regional_trends/top_products_city", paths)
    write_parquet(top_products_by_location(events, products, "state", top_n),
                  "regional_trends/top_products_state", paths)
    write_parquet(top_categories_by_state(events, products, top_n),
                  "regional_trends/top_categories_state", paths)
    write_parquet(location_metrics(events), "regional_trends/location_metrics", paths)
    print("[M1] Regional trend outputs written.")


def main() -> None:
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    top_n = config.get("analytics", {}).get("regional", {}).get("top_n", 10)
    spark = build_spark_session("Module1-RegionalTrends")
    try:
        events = load_cleaned_events(spark, paths)
        products = load_products(spark, paths)
        run(events, products, top_n, paths)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
