# spark/supply/mismatch_detector.py
"""Module 3 (Phase 9): Supply-demand mismatch analysis.

Formula (docs/Memory.md 5.2, PRD FR-11..FR-13):

    SDR = available_stock / (demand_score * K_scale + 1)

    SDR < sdr_low (0.5)  -> HIGH_DEMAND_LOW_STOCK   (critical shortage)
    sdr_low <= SDR <= sdr_high (0.5..2.0) -> BALANCED
    SDR > sdr_high (2.0) -> LOW_DEMAND_HIGH_STOCK   (excess inventory)

K_scale maps the 0-1 demand score to expected weekly unit velocity and
thresholds come from config/pipeline_config.yaml (Rules.md 2.4).

The `+ 1` denominator term guarantees no division by zero even when
demand_score = 0 (Rules.md 6.4 safe division).

Joins demand scores with the inventory snapshot on (product_id, city)
(FR-11). Cities present in demand but absent from inventory get stock 0
-> correctly classified as shortage (missing inventory = no stock).

Output: <processed_base>/supply_demand/
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

from utils.io_helpers import get_storage_paths, load_pipeline_config, read_raw_csv, read_processed, write_parquet  # noqa: E402
from utils.spark_session import build_spark_session  # noqa: E402


def load_inventory(spark: SparkSession, paths: dict) -> DataFrame:
    """Load Member 1's inventory snapshot (one row per product+city)."""
    inv = (read_raw_csv(spark, "inventory", paths)
           .withColumn("product_id", F.trim(F.col("product_id")))
           .withColumn("city", F.trim(F.col("city")))
           .withColumn("available_stock", F.col("available_stock").cast("int")))
    # Aggregate in case multiple snapshot dates exist; latest date wins.
    from pyspark.sql import Window
    latest_date = F.max("date").over(Window.partitionBy())
    inv = inv.withColumn("__latest", latest_date).filter(F.col("date") == F.col("__latest"))
    return inv.groupBy("product_id", "city").agg(F.sum("available_stock").alias("available_stock"))


def compute_mismatch(demand_scores: DataFrame, inventory: DataFrame,
                     k_scale: float, sdr_low: float, sdr_high: float) -> DataFrame:
    """Join demand with stock, compute SDR and classification status."""
    joined = demand_scores.join(inventory, on=["product_id", "city"], how="left")
    joined = joined.withColumn("available_stock",
                               F.coalesce(F.col("available_stock"), F.lit(0)))

    with_sdr = joined.withColumn(
        "stock_to_demand_ratio",
        F.round(F.col("available_stock") / (F.col("demand_score") * F.lit(k_scale) + F.lit(1.0)), 3))

    # Documented guard (Rules.md 6.4): with demand_score = 0 and stock = 0 the raw
    # SDR is 0, which would mislabel "nothing to sell, nothing in stock" as a
    # shortage. Such pairs are reported as BALANCED (no action possible).
    return with_sdr.withColumn(
        "status",
        F.when((F.col("demand_score") == 0) & (F.col("available_stock") == 0), "BALANCED")
         .when(F.col("stock_to_demand_ratio") < F.lit(sdr_low), "HIGH_DEMAND_LOW_STOCK")
         .when(F.col("stock_to_demand_ratio") > F.lit(sdr_high), "LOW_DEMAND_HIGH_STOCK")
         .otherwise("BALANCED")
    ).select("product_id", "product_name", "city", "demand_score", "searches",
             "carts", "purchases", "available_stock", "stock_to_demand_ratio", "status")


def run(demand_scores: DataFrame, inventory: DataFrame, config: dict,
        paths: dict) -> DataFrame:
    """Compute mismatch table and persist it. Returns the result DataFrame."""
    mismatch_cfg = config.get("analytics", {}).get("mismatch", {})
    k_scale = float(mismatch_cfg.get("k_scale", 100.0))
    sdr_low = float(mismatch_cfg.get("sdr_low", 0.5))
    sdr_high = float(mismatch_cfg.get("sdr_high", 2.0))

    result = compute_mismatch(demand_scores, inventory, k_scale, sdr_low, sdr_high)
    write_parquet(result, "supply_demand", paths)
    print("[M3] Supply-demand mismatch table written.")
    return result


def main() -> None:
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    spark = build_spark_session("Module3-SupplyDemandMismatch")
    try:
        demand_scores = read_processed(spark, "demand_scores", paths)
        inventory = load_inventory(spark, paths)
        run(demand_scores, inventory, config, paths)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
