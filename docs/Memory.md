# Persistent Project Memory & State Log

**Project Title:** Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark  
**Academic Context:** Big Data Analytics (BDA) Academic Mini-Project  
**Last Synchronized:** 2026-09-21  
**Project Status:** Planning / Documentation Complete  

---

## 1. Project Status Summary

- **CURRENT STATUS:** Phases 0–9 complete (Member 1 data+HDFS verified with caveats; Member 2 Spark analytics implemented & tested).
- **COMPLETED:** Phase 2–6 core scripts; Phase 7–9 analytics (`spark/analytics/`, `spark/demand/`, `spark/supply/`) verified 2026-09-29 on 1M rows.
- **CURRENT PHASE:** Phase 10 (temporal analytics) not started; Member 2 handoff items 1–9 done.
- **APPLICATION IMPLEMENTATION STATUS:** Local-mode pipeline end-to-end operational; HDFS path **NOT VERIFIED** (no Hadoop installed on dev machine).
- **MEMBER 1 AUDIT (2026-09-29):** generation/Faker/schema/validation/scaling COMPLETE; `hdfs_upload.py` was a stub (real `hdfs dfs` calls commented out) → **FIXED** (real mkdir/put/-ls with honest exit-1 when `hdfs` CLI absent); 10M scale **AT RISK** (events built as Python list in RAM).


---

## 2. Core Project Objective

To build an academic Big Data Analytics pipeline using Apache Hadoop HDFS for distributed block storage, Apache Spark (PySpark & Spark SQL) for distributed in-memory data processing, and Streamlit + Plotly for interactive business visualization. The system processes synthetic multi-million e-commerce clickstream events to identify hyper-local product trends, detect regional supply-demand mismatches, analyze temporal shopping patterns, and estimate empirical discount price elasticity.

---

## 3. Approved Technology Stack (100% Free & Open-Source)

| Technology Layer | Tool / Framework | License | Role in System |
| :--- | :--- | :--- | :--- |
| **Language** | Python 3.10+ | PSF | Universal language across pipeline, Spark, and UI |
| **Data Generation** | Faker, NumPy, Pandas | MIT / BSD | Synthetic clickstream, product, and inventory generation |
| **Distributed Storage** | Apache Hadoop HDFS (v3.3+) | Apache 2.0 | Distributed block storage for raw logs and processed tables |
| **Distributed Compute**| Apache Spark / PySpark (v3.4+)| Apache 2.0 | Distributed in-memory transformations and Spark SQL |
| **File Format** | Apache Parquet (Snappy) | Apache 2.0 | High-performance columnar intermediate and processed format |
| **Visualization** | Streamlit, Plotly Express | Apache 2.0 / MIT | Interactive dashboard and geospatial mapping |
| **Testing** | pytest | MIT | Automated unit and integration testing |
| **Environment** | Ubuntu/Linux or Windows WSL2 | Open | Primary development and execution environment |

*Strict Policy: Zero paid cloud services (AWS, Azure, GCP), zero paid APIs, and zero unapproved technologies (Kafka, Cassandra, Redis, MongoDB, Elasticsearch).*

---

## 4. Dataset Schemas & Relationships

### 4.1 Entities
1. **`events` (Clickstream & Purchases):**
   - `event_id` (String / UUID, PK)
   - `user_id` (String)
   - `product_id` (String, FK $\rightarrow$ `products.product_id`)
   - `timestamp` (Timestamp, ISO 8601)
   - `event_type` (String: `search`, `view`, `cart`, `purchase`)
   - `city` (String)
   - `state` (String)
   - `latitude` (Double)
   - `longitude` (Double)
   - `price` (Double)
   - `discount_percent` (Double: 0.0 to 70.0)
   - `quantity` (Integer)

2. **`products` (Product Dimension Catalog):**
   - `product_id` (String, PK)
   - `product_name` (String)
   - `category` (String)
   - `base_price` (Double)

3. **`inventory` (Regional Warehouse Snapshot):**
   - `product_id` (String, FK $\rightarrow$ `products.product_id`)
   - `city` (String)
   - `available_stock` (Integer)
   - `date` (Date, `YYYY-MM-DD`)

### 4.2 Target Generation Scales
- **Development Scale:** ~100,000 events (quick unit tests)
- **Demonstration Scale:** 1,000,000 to 5,000,000 events (viva defense)
- **Benchmark Scale:** 10,000,000+ events (scalability profiling)

---

## 5. Documented Mathematical & Analytical Formulas

### 5.1 Demand Score Formulation (Module 2)
The Demand Score represents consumer purchase intent across the e-commerce funnel. To prevent high-volume top-of-funnel events (`view`, `search`) from overwhelming low-volume conversion events (`purchase`), each action frequency is min-max normalized across products within the target region/category partition:

$$\tilde{A}_i = \frac{A_i - \min(A)}{\max(A) - \min(A) + \epsilon}$$

The composite **Demand Score** is computed as:

$$\text{Demand Score} = w_s \cdot \tilde{S} + w_v \cdot \tilde{V} + w_c \cdot \tilde{C} + w_p \cdot \tilde{P}$$

**Approved Weights:**
- $w_s = 0.15$ (Searches: Top-of-funnel discovery)
- $w_v = 0.20$ (Views: Active interest)
- $w_c = 0.30$ (Cart Additions: High purchase intent)
- $w_p = 0.35$ (Purchases: Completed economic conversion)
- $\sum w = 1.00$

### 5.2 Stock-to-Demand Ratio & Mismatch Index (Module 3)
To assess regional supply health, the available warehouse inventory is compared against the scaled demand score:

$$SDR = \frac{\text{Available Stock}}{\text{Demand Score} \times K_{\text{scale}} + 1}$$

*(where $K_{\text{scale}}$ maps the 0–1 score to expected weekly unit velocity).*

**State Classifications:**
- **Critical Shortage:** $SDR < 0.5$ (High stockout vulnerability $\rightarrow$ Urgent Restock Alert)
- **Balanced Supply:** $0.5 \le SDR \le 2.0$ (Healthy operational buffer)
- **Excess Inventory:** $SDR > 2.0$ (Capital lockup $\rightarrow$ Promotional Discount Alert)

### 5.3 Empirical Price Elasticity of Demand (Module 6)
Price elasticity of demand is modeled using the academic **Midpoint Arc Elasticity** formulation to ensure symmetry between price increases and decreases:

$$E_d = \frac{\% \Delta Q}{\% \Delta P} = \frac{(Q_2 - Q_1) / \left(\frac{Q_1 + Q_2}{2}\right)}{(P_2 - P_1) / \left(\frac{P_1 + P_2}{2}\right)}$$

- $P_1, P_2$: Effective price (after discount percentage) across two observation brackets.
- $Q_1, Q_2$: Aggregated quantity sold in those respective price brackets.

**Analytical Limitations & Assumptions:**
- *ASSUMPTION:* This is an empirical academic approximation using synthetic observation bands; it assumes ceteris paribus (all other demand factors held constant).
- *Boundary Guard:* If $P_1 = P_2$, elasticity is tagged as undefined (`null`). Extreme synthetic outliers ($|E_d| > 10$) are clamped or flagged as noise.

---

## 6. Project Phase Progress Log

- **Phase 0: Project Initialization** $\rightarrow$ **COMPLETED**
- **Phase 1: Requirements & Documentation** $\rightarrow$ **COMPLETED**
- **Phase 2: Environment Setup & Configuration** $\rightarrow$ **COMPLETED**
- **Phase 3: Synthetic Dataset Generation** $\rightarrow$ **COMPLETED**
- **Phase 4: Data Validation & Local Preprocessing** $\rightarrow$ **COMPLETED**
- **Phase 5: HDFS Cluster Integration & Storage** $\rightarrow$ **COMPLETED**
- **Phase 6: Spark / PySpark Infrastructure Setup** $\rightarrow$ **COMPLETED**
- **Phase 7: Regional Trend Analytics** $\rightarrow$ **COMPLETED** (2026-09-29; `regional_trends.py` + `spark_sql_queries.py`, 22 pytest tests pass)
- **Phase 8: Demand Scoring Engine** $\rightarrow$ **COMPLETED** (2026-09-29; `demand_scorer.py`, hand-computed assertions pass)
- **Phase 9: Supply-Demand Mismatch Analysis** $\rightarrow$ **COMPLETED** (2026-09-29; `mismatch_detector.py`, 3-class status verified)
- **Phase 10: Multi-Granular Temporal Analytics** $\rightarrow$ **NOT STARTED**
- **Phase 11: Discount Analytics** $\rightarrow$ **NOT STARTED**
- **Phase 12: Price Elasticity Modeling** $\rightarrow$ **NOT STARTED**
- **Phase 13: Recommendation Engine** $\rightarrow$ **NOT STARTED**
- **Phase 14: Streamlit + Plotly Dashboard** $\rightarrow$ **NOT STARTED**
- **Phase 15: Pipeline Integration Testing** $\rightarrow$ **NOT STARTED**
- **Phase 16: Performance & Scalability Benchmarking** $\rightarrow$ **NOT STARTED**
- **Phase 17: Viva Documentation & Screenshots** $\rightarrow$ **NOT STARTED**
- **Phase 18: Final Presentation & Defense** $\rightarrow$ **NOT STARTED**

---

## 7. Team Responsibility Matrix

| Team Member | Functional Area | Deliverables & Code Modules |
| :--- | :--- | :--- |
| **Team Member 1** | Data Engineering & HDFS | `scripts/data_generation/`, `hdfs/`, raw data validation, HDFS directory setup, Parquet conversion |
| **Team Member 2** | Big Data Processing & Spark | `spark/preprocessing/`, `spark/analytics/`, `spark/demand/`, `spark/supply/`, Catalyst tuning, benchmarking |
| **Team Member 3** | Business Analytics & Visualization | `spark/pricing/` (elasticity & recommendations), `dashboard/` (Streamlit, Plotly charts, UI/UX components) |

---

## 8. Architectural Decisions Log

| Decision ID | Decision Taken | Rationale | Alternatives Considered |
| :--- | :--- | :--- | :--- |
| **AD-001** | Use synthetic data generated via Python/Faker instead of Kaggle datasets | E-commerce clickstream datasets on Kaggle rarely combine geo-coordinates, event funnels, inventory levels, and discount rates within a unified schema. | Public Kaggle e-commerce datasets (rejected due to missing inventory/geo attributes). |
| **AD-002** | Store intermediate and processed data in Apache Parquet | Columnar format with Snappy compression minimizes disk footprint and enables column pruning in Spark SQL and Streamlit. | CSV (rejected: high I/O overhead, no embedded schema); JSON (rejected: slow parsing). |
| **AD-003** | Use Broadcast Hash Join for `products` dimension | The product catalog (~5,000 items) easily fits in memory; broadcasting avoids expensive network shuffle across worker nodes. | Sort Merge Join (rejected: unnecessary shuffle overhead for small dimension tables). |
| **AD-004** | Decouple Spark processing from Streamlit dashboard serving | Running live Spark jobs on user interaction causes high latency (>30s per click). Pre-aggregating into Parquet enables instant dashboard loading (<2s). | Direct JDBC/Thrift server connection from UI to Spark (rejected: slow, fragile for demo). |
| **AD-005** | Support dual storage mode (HDFS with Local Filesystem fallback) | Allows flexible development and testing on machines where Hadoop services may not be continuously running. | HDFS-only requirement (rejected: risks blocking teammates during local UI prototyping). |

---

## 9. Assumptions Log

- **ASSUMPTION-001:** Geographic coordinates are mapped to major urban commerce hubs in India (e.g., Mumbai, Bengaluru, Delhi NCR, Hyderabad, Chennai, Kolkata, Pune) to ensure realistic spatial clustering.
- **ASSUMPTION-002:** User conversion rates follow a standard e-commerce funnel drop-off ($Search \approx 50\%, View \approx 30\%, Cart \approx 15\%, Purchase \approx 5\%$).
- **ASSUMPTION-003:** Price elasticity is treated as an empirical analytical approximation over grouped discount brackets rather than an econometric causal model.
- **ASSUMPTION-004:** Available inventory represents daily warehouse opening stock and is decremented by purchase aggregations.
- **ASSUMPTION-005 (`k_scale = 100.0`):** A demand score of 1.0 corresponds to ~100 units of expected weekly velocity in the SDR denominator. Value is configurable (`config/pipeline_config.yaml` → `analytics.mismatch.k_scale`); not derived from data. Sensitivity: raising `k_scale` shifts more pairs into `LOW_DEMAND_HIGH_STOCK`.
- **ASSUMPTION-006:** Demand normalization partitions are **(city)**, not (category × city) — sufficient for the FR-10 "per region" requirement given the 8-city fixture.

---

## 10. Important File Locations

- **Requirements & Scope:** `docs/PRD.md`
- **System Architecture:** `docs/Architecture.md`
- **Development Rules:** `docs/Rules.md`
- **Phase Roadmap:** `docs/Phases.md`
- **Dashboard UI Design:** `docs/Design.md`
- **Persistent State:** `docs/Memory.md`

---

## 11. Empirical Verification & Performance Metrics

- **Spark Job Execution Times:** Full Member 2 chain (`spark/run_spark_analytics.py`, 1M events, 5k products, 40k inventory, local[4], Java 22 + PySpark 4.2): **~57 s** measured 2026-09-29. Dev-scale (100k) generation: ~3 s; demo (1M) generation: ~22.7 s. Test suite (22 tests): ~89 s.
- **Member 1 Data Verification (2026-09-29, 1M rows):** 0 nulls, 0 duplicate `event_id`, 0 FK violations, all timestamps parse `yyyy-MM-dd HH:mm:ss`, discount ∈ [0,70], coordinates within India bounds, `validate_records.py` exit 0 ("100% passed").
- **Member 2 Output Volumes (1M rows):** `demand_scores` 40,000 rows (score range 0.0693–0.7729); `supply_demand` 40,000 rows (status split: 4,916 `HIGH_DEMAND_LOW_STOCK` / 3,990 `BALANCED` / 31,094 `LOW_DEMAND_HIGH_STOCK`); 16 Parquet files under `data/processed/`. Note: excess skew toward `LOW_DEMAND_HIGH_STOCK` reflects real data (purchases ≈ 10% of events vs. stock up to 450 units), not a hardcoded classification.
- **HDFS Block Distribution:** NOT VERIFIED — no Hadoop installed on this machine (`hdfs` CLI absent); `hdfs_upload.py` HDFS branch tested to fail with exit 1 rather than fake success.
- **Data Compression Ratio:** NOT YET CALCULATED (Parquet outputs exist but ratio not measured).
- **Elasticity Summary by Category:** NOT YET CALCULATED (Awaiting Phase 12).
- **Known Bugs / Defects:**
  - 10M-event generation may OOM (`generate_events.py` materializes a Python list of dicts before DataFrame conversion) — **NOT TESTED** at 10M.
  - `process_regional_trends.py` still hardcodes `hdfs://localhost:9000` (Rules 2.4 violation; legacy, superseded by config-driven `spark/analytics/`).

---

## 12. Immediate Next Steps

1. Run `python scripts/run_pipeline.py` then `python spark/run_spark_analytics.py` from repo root (requires `HADOOP_HOME=C:\hadoop`, `PYSPARK_PYTHON=python`, `C:\hadoop\bin` on PATH — set as user env vars 2026-09-29).
2. Phase 10–13 (temporal / discount / elasticity / recommendations) not started — owner: Members 2/3 per responsibility matrix.
3. HDFS verification: install Hadoop 3.3.6 per README Part 1, set `storage.type: hdfs`, run `python hdfs/hdfs_upload.py` (now executes real `hdfs dfs` commands and fails loudly if unavailable) — **currently NOT VERIFIED**.
4. Test 10M benchmark scale before claiming FR-03 benchmark mode (possible OOM, see §11).
5. Add `spark/pricing/` and dashboard only when Phases 11–14 are picked up.
