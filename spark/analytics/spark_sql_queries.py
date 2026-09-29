# spark/analytics/spark_sql_queries.py
"""Module 1b: Equivalent analytics expressed with Spark SQL.

Demonstrates meaningful Spark SQL usage (PRD/Architecture 5.2): the same
core aggregations as the DataFrame API, run through temporary views and
spark.sql() - showing the Catalyst optimizer path is exercised.

Queries (all distributed, no driver-side collect of event data):
1. top_products_city_sql     - top purchased products per city (FR-05)
2. top_categories_state_sql  - GMV by category per state (FR-06)
3. event_mix_by_city_sql     - funnel mix per city (FR-07 support)
4. hourly_purchase_sql       - purchase counts by hour (supports Phase 10)

Outputs -> <processed_base>/regional_trends/*_sql/
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

from utils.io_helpers import get_storage_paths, load_pipeline_config, read_processed, read_raw_csv, write_parquet  # noqa: E402
from utils.spark_session import build_spark_session  # noqa: E402

QUERIES: dict[str, str] = {
    "top_products_city_sql": """
        SELECT city, event_type, product_id, product_name, event_count, rank
        FROM (
            SELECT e.city,
                   e.event_type,
                   e.product_id,
                   p.product_name,
                   COUNT(*) AS event_count,
                   DENSE_RANK() OVER (PARTITION BY e.city, e.event_type
                                       ORDER BY COUNT(*) DESC) AS rank
            FROM events e
            LEFT JOIN products p ON e.product_id = p.product_id
            GROUP BY e.city, e.event_type, e.product_id, p.product_name
        ) t
        WHERE rank <= {top_n}
    """,
    "top_categories_state_sql": """
        SELECT state, category, purchase_orders, gmv, rank
        FROM (
            SELECT e.state,
                   p.category,
                   COUNT(*) AS purchase_orders,
                   SUM(e.price * e.quantity) AS gmv,
                   RANK() OVER (PARTITION BY e.state
                                ORDER BY SUM(e.price * e.quantity) DESC) AS rank
            FROM events e
            JOIN products p ON e.product_id = p.product_id
            WHERE e.event_type = 'purchase'
            GROUP BY e.state, p.category
        ) t
        WHERE rank <= {top_n}
    """,
    "event_mix_by_city_sql": """
        SELECT city,
               SUM(CASE WHEN event_type = 'search'   THEN 1 ELSE 0 END) AS searches,
               SUM(CASE WHEN event_type = 'view'     THEN 1 ELSE 0 END) AS views,
               SUM(CASE WHEN event_type = 'cart'     THEN 1 ELSE 0 END) AS carts,
               SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
               COUNT(*) AS total_events
        FROM events
        GROUP BY city
        ORDER BY total_events DESC
    """,
    "hourly_purchase_sql": """
        SELECT HOUR(timestamp) AS hour_of_day,
               COUNT(*) AS purchases,
               SUM(price * quantity) AS revenue
        FROM events
        WHERE event_type = 'purchase'
        GROUP BY HOUR(timestamp)
        ORDER BY hour_of_day
    """,
}


def run(spark: SparkSession, paths: dict, top_n: int) -> None:
    """Register views and execute the SQL analytics suite."""
    events = read_processed(spark, "cleaned/events", paths)
    products = (read_raw_csv(spark, "products", paths)
                .withColumn("product_id", F.trim(F.col("product_id"))))
    events.createOrReplaceTempView("events")
    products.createOrReplaceTempView("products")

    for name, sql in QUERIES.items():
        print(f"[SQL] Running {name} ...")
        df: DataFrame = spark.sql(sql.format(top_n=top_n))
        module = name if name.startswith("event_mix") or name.startswith("hourly") \
            else f"regional_trends/{name}"
        out = write_parquet(df, module, paths)
        print(f"[SQL] {name} -> {out} ({df.count()} rows)")


def main() -> None:
    config = load_pipeline_config()
    paths = get_storage_paths(config)
    top_n = config.get("analytics", {}).get("regional", {}).get("top_n", 10)
    spark = build_spark_session("Module1b-SparkSQL")
    try:
        run(spark, paths, top_n)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
