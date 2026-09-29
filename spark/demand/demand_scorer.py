# spark/demand/demand_scorer.py
"""Module 2 (Phase 8): Weighted demand scoring engine.

Formula (docs/Memory.md 5.1, PRD FR-09/FR-10):

    ~A_i = (A_i - min(A)) / (max(A) - min(A) + eps)      # min-max normalize
    Demand Score = 0.15*~search + 0.20*~view + 0.30*~cart + 0.35*purchase

Normalization runs per product within each (city) partition so raw funnel
volumes of big cities do not drown low-volume locations (FR-10). All four
event types are supported by Member 1's schema (event_type =
search|view|cart|purchase), so the documented weights apply as-is.

Score is bounded in [0, 1] by construction. Weights and eps come from
config/pipeline_config.yaml (Rules.md 2.4 - no hardcoded constants).

Output columns: product_id, product_name, city, searches, views, carts,
purchases, demand_score  -> <processed_base>/demand_scores/
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


def compute_demand_scores(events: DataFrame, products: DataFrame,
                          weights: dict, eps: float) -> DataFrame:
    """Compute the composite Demand Score per (product, city).

    Steps: funnel counts -> min-max normalization within city ->
    weighted sum using documented weights.
    """
    funnel_counts = (events.groupBy("product_id", "city")
                     .agg(*[
                         F.sum(F.when(F.col("event_type") == et, 1).otherwise(0)).alias(c)
                         for et, c in (("search", "searches"), ("view", "views"),
                                       ("cart", "carts"), ("purchase", "purchases"))
                     ]))

    # Min-max normalize each funnel column across products within a city (FR-10).
    by_city = Window.partitionBy("city")
    normalized = funnel_counts
    for col_name in ("searches", "views", "carts", "purchases"):
        mn = F.min(col_name).over(by_city)
        mx = F.max(col_name).over(by_city)
        normalized = normalized.withColumn(
            f"n_{col_name}", (F.col(col_name) - mn) / (mx - mn + F.lit(eps)))

    scored = normalized.withColumn(
        "demand_score",
        F.round(
            F.lit(weights["search"]) * F.col("n_searches")
            + F.lit(weights["view"]) * F.col("n_views")
            + F.lit(weights["cart"]) * F.col("n_carts")
            + F.lit(weights["purchase"]) * F.col("n_purchases"), 4))

    result = (scored.join(F.broadcast(products.select("product_id", "product_name")),
                          "product_id", "left")
              .select("product_id", "product_name", "city", "searches", "views",
                      "carts", "purchases", "demand_score"))
    return result


def run(events: DataFrame, products: DataFrame, config: dict, paths: dict) -> DataFrame:
    """Compute demand scores and persist them. Returns the score DataFrame."""
    analytics = config.get("analytics", {})
    weights = analytics.get("weights", {"search": 0.15, "view": 0.20,
                                        "cart": 0.30, "purchase": 0.35})
    eps = float(analytics.get("normalization_epsilon", 1e-6))

    scores = compute_demand_scores(events, products, weights, eps)
    write_parquet(scores, "demand_scores", paths)
    print("[M2] Demand scores written.")
    return scores


def main() -> None:
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    spark = build_spark_session("Module2-DemandScoring")
    try:
        from utils.io_helpers import read_raw_csv
        events = read_processed(spark, "cleaned/events", paths)
        products = (read_raw_csv(spark, "products", paths)
                    .withColumn("product_id", F.trim(F.col("product_id"))))
        run(events, products, config, paths)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
