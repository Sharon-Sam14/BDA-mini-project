# spark/preprocessing/clean_events.py
"""Phase 4 / Member 2: PySpark data cleaning and type normalization.

Reads Member 1's raw CSVs, enforces documented bounds, quarantines
invalid records with a stated reason for every dropped row, and writes
cleaned Parquet to <processed_base>/cleaned/events.

Documented cleaning decisions (Rules.md 3.3 - no silent deletion):
- Exact duplicate event_id rows -> DROPPED (keep first): re-running the
  generator can regenerate identical ids; duplicates inflate funnel counts.
- Missing user_id / product_id / city / timestamp -> QUARANTINED
  (unrecoverable; blocks joins and regional grouping).
- price <= 0, discount outside 0-70%, quantity <= 0, coordinates outside
  India bounds (lat 8-38, lon 68-98) -> QUARANTINED (same rule set as
  spark/preprocessing/validate_records.py).
- event_type outside {search, view, cart, purchase} -> QUARANTINED
  (unknown funnel stage cannot be scored).
- product_id not in the products catalog -> QUARANTINED (broken FK).
- Strings trimmed; timestamp cast to TimestampType; numerics cast to
  their schema types. Quarantined rows are preserved at
  <processed_base>/quarantine/events for audit, never silently deleted.
"""
from __future__ import annotations

import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

_SPARK_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_SPARK_ROOT), str(_SPARK_ROOT.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils.io_helpers import get_storage_paths, load_pipeline_config, read_raw_csv, write_parquet  # noqa: E402
from utils.spark_session import build_spark_session  # noqa: E402

VALID_EVENT_TYPES = ["search", "view", "cart", "purchase"]


def build_products(spark: SparkSession, paths: dict) -> DataFrame:
    """Load and type-cast the product dimension table."""
    return (read_raw_csv(spark, "products", paths)
            .withColumn("product_id", F.trim(F.col("product_id")))
            .withColumn("base_price", F.col("base_price").cast("double")))


def clean_events(events_raw: DataFrame, products: DataFrame
                 ) -> tuple[DataFrame, DataFrame, DataFrame, int]:
    """Clean raw events.

    Returns (clean_df, quarantine_df, rejected_counts_by_reason, dup_count).
    """
    # --- Cast + trim -----------------------------------------------------
    df = (events_raw
          .withColumn("event_id", F.trim(F.col("event_id")))
          .withColumn("user_id", F.trim(F.col("user_id")))
          .withColumn("product_id", F.trim(F.col("product_id")))
          .withColumn("event_type", F.lower(F.trim(F.col("event_type"))))
          .withColumn("city", F.trim(F.col("city")))
          .withColumn("state", F.trim(F.col("state")))
          # try_to_timestamp returns NULL on bad input (Spark 4 to_timestamp throws),
          # so invalid timestamps are quarantined below instead of failing the job.
          .withColumn("timestamp",
                      F.try_to_timestamp("timestamp", F.lit("yyyy-MM-dd HH:mm:ss")))
          .withColumn("latitude", F.col("latitude").cast("double"))
          .withColumn("longitude", F.col("longitude").cast("double"))
          .withColumn("price", F.col("price").cast("double"))
          .withColumn("discount_percent", F.col("discount_percent").cast("int"))
          .withColumn("quantity", F.col("quantity").cast("int")))

    total_in = df.count()

    # --- Deduplicate (keep first occurrence) -----------------------------
    df = df.dropDuplicates(["event_id"])
    dup_count = total_in - df.count()

    # --- Foreign-key flag via broadcast left join (no collect) -----------
    valid_product_ids = products.select("product_id").distinct()
    df = df.join(F.broadcast(valid_product_ids.withColumn("__valid_fk", F.lit(True))),
                 on="product_id", how="left")

    # --- Validation / quarantine classification --------------------------
    # First matching rule wins; order = severity order (identity -> funnel -> bounds -> FK).
    quarantine_reason = (
        F.when(F.col("event_id").isNull() | (F.col("event_id") == ""), "NULL_EVENT_ID")
        .when(F.col("user_id").isNull() | (F.col("user_id") == ""), "NULL_USER_ID")
        .when(F.col("product_id").isNull() | (F.col("product_id") == ""), "NULL_PRODUCT_ID")
        .when(F.col("timestamp").isNull(), "BAD_TIMESTAMP")
        .when(~F.col("event_type").isin(VALID_EVENT_TYPES), "BAD_EVENT_TYPE")
        .when(F.col("city").isNull() | (F.col("city") == ""), "NULL_CITY")
        .when(F.col("price").isNull() | (F.col("price") <= 0), "BAD_PRICE")
        .when(F.col("discount_percent").isNull()
              | (F.col("discount_percent") < 0) | (F.col("discount_percent") > 70),
              "BAD_DISCOUNT")
        .when(F.col("quantity").isNull() | (F.col("quantity") <= 0), "BAD_QUANTITY")
        .when(F.col("latitude").isNull() | (F.col("longitude").isNull())
              | (F.col("latitude") < 8.0) | (F.col("latitude") > 38.0)
              | (F.col("longitude") < 68.0) | (F.col("longitude") > 98.0),
              "BAD_COORDINATES")
        .when(F.col("__valid_fk").isNull(), "BROKEN_FK_PRODUCT")
        .otherwise(F.lit(None).cast("string"))
    ).alias("quarantine_reason")

    df = df.withColumn("quarantine_reason", quarantine_reason)
    quarantine_df = df.filter(F.col("quarantine_reason").isNotNull())
    clean_df = df.filter(F.col("quarantine_reason").isNull()).drop(
        "quarantine_reason", "__valid_fk")

    rejected_counts = (quarantine_df.groupBy("quarantine_reason").count()
                       .orderBy(F.desc("count")))

    if dup_count:
        print(f"[CLEAN] Dropped {dup_count} duplicate event_id rows (keep first).")
    print(f"[CLEAN] Input rows: {total_in} | clean: {clean_df.count()} | "
          f"quarantined: {quarantine_df.count()}")
    return clean_df, quarantine_df, rejected_counts, dup_count


def main() -> None:
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    spark = build_spark_session("Phase4-DataCleaning")
    try:
        events_raw = read_raw_csv(spark, "events", paths)
        products = build_products(spark, paths)
        clean_df, quarantine_df, rejected_counts, _ = clean_events(events_raw, products)

        rejected_counts.show(truncate=False)
        out = write_parquet(clean_df, "cleaned/events", paths)
        print(f"[CLEAN] Wrote cleaned events Parquet -> {out}")

        # Quarantine kept separately for auditability (never silently deleted).
        quarantine_path = f"{paths['processed_base']}/quarantine/events"
        (quarantine_df.write.mode("overwrite").option("compression", "snappy")
         .parquet(quarantine_path))
        print(f"[CLEAN] Wrote quarantined rows -> {quarantine_path}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
