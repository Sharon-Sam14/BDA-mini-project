# tests/test_analytics_formulas.py
"""Tests for demand scoring (Module 2) and supply-demand mismatch (Module 3).

Expected values are computed by hand from the documented formulas in
docs/Memory.md 5.1/5.2 - not copied from implementation output.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "spark"))

from pyspark.sql import functions as F

from demand.demand_scorer import compute_demand_scores
from supply.mismatch_detector import compute_mismatch, load_inventory
from utils.io_helpers import read_raw_csv
from preprocessing.clean_events import build_products, clean_events

WEIGHTS = {"search": 0.15, "view": 0.20, "cart": 0.30, "purchase": 0.35}
EPS = 1.0e-6


def _cleaned(spark, fixture_paths):
    raw = read_raw_csv(spark, "events", fixture_paths)
    products = build_products(spark, fixture_paths)
    clean, *_ = clean_events(raw, products)
    return clean, products


def test_demand_score_hand_computed(spark, fixture_paths):
    """Bengaluru PRD_00001 vs PRD_00003 - hand-computed expected scores.

    Bengaluru clean rows (only these 2 products appear in that city):
      PRD_00001: searches=2, views=1, carts=1, purchases=1
      PRD_00003: searches=0, views=1, carts=0, purchases=1
    Min-max normalization within Bengaluru (eps negligible):
      searches: min=0 max=2 -> PRD_00001: 1.0,  PRD_00003: 0.0
      views:    min=1 max=1 -> both 0 (constant column)
      carts:    min=0 max=1 -> PRD_00001: 1.0,  PRD_00003: 0.0
      purchases:min=1 max=1 -> both 0 (constant column)
    Scores: PRD_00001 = 0.15*1 + 0.30*1 = 0.45
            PRD_00003 = 0.00
    """
    events, products = _cleaned(spark, fixture_paths)
    scores = compute_demand_scores(events, products, WEIGHTS, EPS)
    rows = {r["product_id"]: r for r in
            scores.filter(F.col("city") == "Bengaluru").collect()}

    assert rows["PRD_00001"]["searches"] == 2
    assert rows["PRD_00001"]["purchases"] == 1
    assert abs(rows["PRD_00001"]["demand_score"] - 0.45) < 0.001
    assert abs(rows["PRD_00003"]["demand_score"] - 0.0) < 0.001


def test_demand_score_bounded_and_weighted(spark, fixture_paths):
    """All scores in [0,1]; weights sum to 1.0 (FR-09)."""
    events, products = _cleaned(spark, fixture_paths)
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
    scores = compute_demand_scores(events, products, WEIGHTS, EPS)
    stats = scores.agg(F.min("demand_score"), F.max("demand_score")).first()
    assert stats[0] >= 0.0
    assert stats[1] <= 1.0


def test_demand_score_covers_all_regions_products(spark, fixture_paths):
    events, products = _cleaned(spark, fixture_paths)
    scores = compute_demand_scores(events, products, WEIGHTS, EPS)
    # every product/city pair present in cleaned events appears in scores
    pairs = events.select("product_id", "city").distinct().count()
    assert scores.count() == pairs
    assert {"product_id", "product_name", "city", "searches", "views",
            "carts", "purchases", "demand_score"} == set(scores.columns)


def test_supply_demand_status_classification(spark, fixture_paths):
    """Hand-computed SDR/status for Bengaluru using K_scale=100, bounds 0.5/2.0.

    PRD_00001: demand=0.45, stock=5   -> SDR = 5/(0.45*100+1)   = 0.109 -> HIGH_DEMAND_LOW_STOCK
    PRD_00003: demand=0.00, stock=400 -> SDR = 400/(0.00*100+1) = 400.0 -> LOW_DEMAND_HIGH_STOCK
    """
    events, products = _cleaned(spark, fixture_paths)
    scores = compute_demand_scores(events, products, WEIGHTS, EPS)
    inventory = load_inventory(spark, fixture_paths)
    result = compute_mismatch(scores, inventory, k_scale=100.0,
                              sdr_low=0.5, sdr_high=2.0)
    rows = {r["product_id"]: r for r in
            result.filter(F.col("city") == "Bengaluru").collect()}

    r1 = rows["PRD_00001"]
    assert r1["status"] == "HIGH_DEMAND_LOW_STOCK"
    assert abs(r1["stock_to_demand_ratio"] - 5 / (0.45 * 100 + 1)) < 0.01

    r3 = rows["PRD_00003"]
    assert r3["status"] == "LOW_DEMAND_HIGH_STOCK"
    assert abs(r3["stock_to_demand_ratio"] - 400 / (0.0 * 100 + 1)) < 0.01


def test_supply_demand_statuses_cover_three_classes(spark, fixture_paths):
    events, products = _cleaned(spark, fixture_paths)
    scores = compute_demand_scores(events, products, WEIGHTS, EPS)
    inventory = load_inventory(spark, fixture_paths)
    result = compute_mismatch(scores, inventory, 100.0, 0.5, 2.0)
    statuses = {r["status"] for r in result.select("status").distinct().collect()}
    assert statuses == {"HIGH_DEMAND_LOW_STOCK", "BALANCED", "LOW_DEMAND_HIGH_STOCK"}


def test_sdr_safe_against_zero_demand_and_stock(spark, fixture_paths):
    """demand=0 & stock=0 must not divide by zero nor claim a shortage."""
    events, products = _cleaned(spark, fixture_paths)
    zero_demand = compute_mismatch(
        events.select("product_id", "city").distinct()
              .withColumn("product_name", F.lit("x"))
              .withColumn("demand_score", F.lit(0.0))
              .withColumn("searches", F.lit(0)).withColumn("carts", F.lit(0))
              .withColumn("purchases", F.lit(0)),
        load_inventory(spark, fixture_paths).withColumn(
            "available_stock", F.lit(0)),
        100.0, 0.5, 2.0)
    statuses = [r["status"] for r in zero_demand.collect()]
    assert statuses and all(s == "BALANCED" for s in statuses)
    assert all(r["stock_to_demand_ratio"] == 0.0 for r in zero_demand.collect())
