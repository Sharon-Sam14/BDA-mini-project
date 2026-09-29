# spark/utils/io_helpers.py
"""Config-driven storage helpers for the Spark analytics layer.

Resolves raw/processed locations from config/pipeline_config.yaml so no
module hard-codes filesystem or HDFS paths (Rules.md 2.4).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml
from pyspark.sql import DataFrame, SparkSession

# Allow `python spark/<module>/script.py` execution from the repo root.
_SPARK_ROOT = Path(__file__).resolve().parents[1]
if str(_SPARK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SPARK_ROOT))

DEFAULT_CONFIG_PATH = "config/pipeline_config.yaml"


def load_pipeline_config(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Load pipeline YAML config; fall back to local defaults if absent."""
    if not os.path.exists(config_path):
        return {
            "storage": {
                "type": "local",
                "local": {"raw_base": "data/raw", "processed_base": "data/processed"},
            },
            "analytics": {},
        }
    with open(config_path, "r") as handle:
        return yaml.safe_load(handle)


def get_storage_paths(config: dict | None = None) -> dict:
    """Return {'mode', 'raw_base', 'processed_base'} for the active backend.

    local mode -> repo-relative ./data/... paths.
    hdfs mode  -> /ecommerce/... paths (fs.defaultFS from the Hadoop config).
    """
    config = config or load_pipeline_config()
    storage = config["storage"]
    mode = storage.get("type", "local").lower()
    if mode == "hdfs":
        section = storage["hdfs"]
    else:
        section = storage["local"]
        mode = "local"
    return {
        "mode": mode,
        "raw_base": section["raw_base"],
        "processed_base": section["processed_base"],
    }


def raw_csv_path(entity: str, paths: dict) -> str:
    """Path of a raw CSV entity (events|products|inventory)."""
    return f"{paths['raw_base']}/{entity}/{entity}.csv"


def processed_dir(module_name: str, paths: dict) -> str:
    """Output directory for a processed analytical module."""
    return f"{paths['processed_base']}/{module_name}"


def read_raw_csv(spark: SparkSession, entity: str, paths: dict) -> DataFrame:
    """Read a raw CSV (header row, all columns as strings; casting happens in cleaning)."""
    return spark.read.option("header", True).csv(raw_csv_path(entity, paths))


def read_processed(spark: SparkSession, module_name: str, paths: dict) -> DataFrame:
    """Read a previously written processed Parquet dataset."""
    return spark.read.parquet(processed_dir(module_name, paths))


def write_parquet(df: DataFrame, module_name: str, paths: dict,
                  partition_by: list | None = None) -> str:
    """Write a DataFrame as Snappy Parquet (overwrite) and return the path."""
    target = processed_dir(module_name, paths)
    writer = df.write.mode("overwrite").option("compression", "snappy")
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    writer.parquet(target)
    return target
