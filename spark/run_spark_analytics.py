# spark/run_spark_analytics.py
"""Member 2 entry point: run the full Spark analytics chain in order.

    clean_events -> regional_trends -> spark_sql_queries
                 -> demand_scorer -> mismatch_detector

Consumes Member 1's raw CSVs (data/raw or HDFS /ecommerce/raw via
config/pipeline_config.yaml storage.type) and writes Parquet to
<processed_base>/.

Run from the repo root:
    python spark/run_spark_analytics.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_SPARK_ROOT = Path(__file__).resolve().parent
for _p in (str(_SPARK_ROOT), str(_SPARK_ROOT.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils.io_helpers import get_storage_paths, load_pipeline_config, read_raw_csv, read_processed  # noqa: E402
from utils.spark_session import build_spark_session  # noqa: E402

from preprocessing.clean_events import build_products, clean_events  # noqa: E402
from analytics import regional_trends, spark_sql_queries  # noqa: E402
from demand.demand_scorer import run as run_demand  # noqa: E402
from supply.mismatch_detector import load_inventory, run as run_mismatch  # noqa: E402


def main() -> int:
    os.chdir(Path(__file__).resolve().parents[1])  # cwd-relative paths (repo root)
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    analytics_cfg = config.get("analytics", {})
    top_n = analytics_cfg.get("regional", {}).get("top_n", 10)

    started = time.time()
    spark = build_spark_session("Member2-AnalyticsPipeline")
    try:
        # --- Stage 1: cleaning (Phase 4/Member 2) -----------------------
        print("\n=== STAGE 1: Data cleaning & quarantine ===")
        events_raw = read_raw_csv(spark, "events", paths)
        products_raw = build_products(spark, paths)
        clean_df, quarantine_df, rejected_counts, _ = clean_events(events_raw, products_raw)
        rejected_counts.show(truncate=False)
        from utils.io_helpers import write_parquet
        write_parquet(clean_df, "cleaned/events", paths)
        write_parquet(quarantine_df, "quarantine/events", paths)

        # Re-read persisted cleaned data so every downstream module proves
        # it consumes the stored artifact (not an in-memory shortcut).
        events = read_processed(spark, "cleaned/events", paths)

        # --- Stage 2: Module 1 regional trends (DataFrame API) ----------
        print("\n=== STAGE 2: Regional trends (DataFrame API) ===")
        regional_trends.run(events, products_raw, top_n, paths)

        # --- Stage 3: Module 1b Spark SQL suite -------------------------
        print("\n=== STAGE 3: Spark SQL analytics ===")
        spark_sql_queries.run(spark, paths, top_n)

        # --- Stage 4: Module 2 demand scoring ---------------------------
        print("\n=== STAGE 4: Demand scoring ===")
        scores = run_demand(events, products_raw, config, paths)

        # --- Stage 5: Module 3 supply-demand mismatch -------------------
        print("\n=== STAGE 5: Supply-demand mismatch ===")
        inventory = load_inventory(spark, paths)
        mismatch = run_mismatch(scores, inventory, config, paths)
        mismatch.filter("status = 'HIGH_DEMAND_LOW_STOCK'") \
            .orderBy("stock_to_demand_ratio").show(10, truncate=False)

        elapsed = time.time() - started
        print(f"\n[Member2] Analytics chain completed in {elapsed:.1f}s.")
        print(f"[Member2] Outputs under: {paths['processed_base']}/")
        return 0
    finally:
        spark.stop()


if __name__ == "__main__":
    sys.exit(main())
