# Project Execution Phases & Milestones

**Project Title:** Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark  
**Academic Context:** Big Data Analytics (BDA) Academic Mini-Project  
**Document Version:** 1.0.0  
**Status:** Active Roadmap  

---

## 1. Master Phase Roadmap Overview

| Phase | Title | Lead Owner | Status | Target Completion |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Project Initialization | Lead / All | **COMPLETED** | Day 1 |
| **Phase 1** | Requirements & Core Documentation | Lead / All | **COMPLETED** | Day 1 |
| **Phase 2** | Environment Setup & Configuration | Team Member 1 | **COMPLETED** | Day 2 |
| **Phase 3** | Synthetic Dataset Generation | Team Member 1 | **COMPLETED** | Day 3 |
| **Phase 4** | Data Validation & Local Preprocessing | Team Member 1 | **COMPLETED** | Day 4 |
| **Phase 5** | HDFS Cluster Integration & Storage Layout | Team Member 1 | **COMPLETED** | Day 5 |
| **Phase 6** | Apache Spark / PySpark Infrastructure Setup | Team Member 2 | **COMPLETED** | Day 6 |
| **Phase 7** | Regional Trend & Geo-Spatial Analytics | Team Member 2 | **NOT STARTED** | Day 7 |
| **Phase 8** | Multi-Action Demand Scoring Engine | Team Member 2 | **NOT STARTED** | Day 8 |
| **Phase 9** | Supply-Demand Mismatch Analysis | Team Member 2 | **NOT STARTED** | Day 9 |
| **Phase 10** | Multi-Granular Temporal Analytics | Team Member 2 | **NOT STARTED** | Day 10 |
| **Phase 11** | Discount Banding & Response Analytics | Team Member 3 | **NOT STARTED** | Day 11 |
| **Phase 12** | Empirical Price Elasticity Modeling | Team Member 3 | **NOT STARTED** | Day 12 |
| **Phase 13** | Algorithmic Business Recommendation Engine | Team Member 3 | **NOT STARTED** | Day 13 |
| **Phase 14** | Interactive Streamlit + Plotly Dashboard | Team Member 3 | **NOT STARTED** | Day 15 |
| **Phase 15** | End-to-End Pipeline Integration Testing | Lead / All | **NOT STARTED** | Day 16 |
| **Phase 16** | Performance & Scalability Benchmarking | Team Member 2 | **NOT STARTED** | Day 17 |
| **Phase 17** | Viva Visual Documentation & Screenshots | Team Member 3 | **NOT STARTED** | Day 18 |
| **Phase 18** | Final Presentation & Viva Voce Defense | All Members | **NOT STARTED** | Day 19 |

---

## 2. Detailed Phase Specifications

---

### Phase 0: Project Initialization
- **Status:** **COMPLETED**
- **Objective:** Establish the foundational directory structure, Git configuration, and project scoping.
- **Tasks:**
  - Create directory skeleton conforming to [Architecture.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Architecture.md).
  - Initialize `.gitignore` for Python, Spark logs, virtual environments, and temporary data.
  - Define core scope and technology boundaries.
- **Expected Output:** Clean workspace with structured directories.
- **Dependencies:** None.
- **Completion Criteria:** Root directories `/docs`, `/data`, `/scripts`, `/hdfs`, `/spark`, `/dashboard`, `/tests`, `/notebooks`, `/config` initialized.
- **Testing Requirements:** Verify workspace directory tree and Git status.

---

### Phase 1: Requirements & Core Documentation
- **Status:** **COMPLETED**
- **Objective:** Establish the comprehensive, permanent source-of-truth documentation set.
- **Tasks:**
  - Formulate `PRD.md` with detailed functional and non-functional requirements.
  - Formulate `Architecture.md` with component, HDFS, Spark, and data flow specifications.
  - Formulate `Rules.md` with strict engineering, coding, and zero-hallucination policies.
  - Formulate `Phases.md` outlining the 19 execution stages.
  - Formulate `Design.md` detailing the academic Streamlit + Plotly UI/UX system.
  - Formulate `Memory.md` for project context and state tracking.
- **Expected Output:** All six documentation files created in `/docs/` without contradictions.
- **Dependencies:** Phase 0.
- **Completion Criteria:** All six markdown files verified, aligned with project constraints, and approved.
- **Testing Requirements:** Cross-file link validation and schema consistency review.

---

### Phase 2: Environment Setup & Configuration
- **Status:** **COMPLETED**
- **Objective:** Install and configure the local Python virtual environment, Java runtime, Hadoop binaries, and PySpark dependencies.
- **Tasks:**
  - Setup Python 3.10+ virtual environment (`venv`).
  - Configure `requirements.txt` with pinned versions (`pyspark`, `streamlit`, `plotly`, `faker`, `pandas`, `pyarrow`, `pytest`, `pyyaml`).
  - Verify Java JDK 8 or 11 installation (`JAVA_HOME`).
  - Verify Hadoop binaries (`winutils.exe` on Windows or native Hadoop binaries on Linux/WSL).
  - Create centralized config files (`spark_config.yaml`, `pipeline_config.yaml`).
- **Expected Output:** Working virtual environment with verified Spark, Java, and Python runtimes.
- **Dependencies:** Phase 1.
- **Completion Criteria:** `python -c "import pyspark, streamlit, plotly"` executes with exit code 0.
- **Testing Requirements:** Automated smoke test verifying environment variables (`JAVA_HOME`, `SPARK_HOME`, `HADOOP_HOME`).

---

### Phase 3: Synthetic Dataset Generation
- **Status:** **COMPLETED**
- **Objective:** Develop high-throughput synthetic generators for `products`, `events`, and `inventory`.
- **Tasks:**
  - Implement `scripts/data_generation/geo_metadata.py` with major Indian/global metro coordinates.
  - Implement `scripts/data_generation/generate_products.py` (~5,000 products across 8 categories).
  - Implement `scripts/data_generation/generate_events.py` (~1M to 10M events with realistic funnels: search, view, cart, purchase).
  - Implement `scripts/data_generation/generate_inventory.py` (city-warehouse stock snapshots).
  - Build master orchestration CLI `scripts/data_generation/generate_all.py` supporting `--scale dev|demo|benchmark`.
- **Expected Output:** Synthesized CSV/Parquet files in `data/raw/` or `data/sample/`.
- **Dependencies:** Phase 2.
- **Completion Criteria:** Generation runs without memory exhaustion; outputs meet schema specifications.
- **Testing Requirements:** Unit test `tests/test_data_generation.py` verifying row counts, column types, and foreign key integrity.

---

### Phase 4: Data Validation & Local Preprocessing
- **Status:** **COMPLETED**
- **Objective:** Validate generated raw data quality, bounds, and referential integrity before ingestion.
- **Tasks:**
  - Implement `spark/preprocessing/validate_records.py`.
  - Validate coordinate bounds (latitude/longitude), non-negative pricing, and valid discount percentages (0–70%).
  - Ensure all `events.product_id` and `inventory.product_id` values exist in `products.csv`.
  - Implement logging for quarantine or discard of corrupt records.
- **Expected Output:** Clean, validated staging datasets ready for HDFS storage.
- **Dependencies:** Phase 3.
- **Completion Criteria:** 100% of validated records adhere to declared StructType schemas.
- **Testing Requirements:** Ingestion validation suite testing edge cases (null prices, invalid event types).

---

### Phase 5: HDFS Cluster Integration & Storage Layout
- **Status:** **COMPLETED**
- **Objective:** Provision HDFS directory hierarchy, configure replication, and upload raw data.
- **Tasks:**
  - Write `scripts/hdfs_init.sh` to initialize `/ecommerce/raw/` and `/ecommerce/processed/` in HDFS.
  - Implement Python HDFS upload/download wrappers in `hdfs/hdfs_upload.py`.
  - Ingest raw `events`, `products`, and `inventory` files into HDFS.
  - Implement local filesystem fallback toggle in `config/pipeline_config.yaml` for seamless dual-mode execution.
- **Expected Output:** Populated HDFS storage with deterministic directory paths.
- **Dependencies:** Phase 4.
- **Completion Criteria:** `hdfs dfs -ls -R /ecommerce/raw/` confirms file availability and block allocation.
- **Testing Requirements:** HDFS connection test verifying file existence and read permissions.

---

### Phase 6: Apache Spark / PySpark Infrastructure Setup
- **Status:** **COMPLETED**
- **Objective:** Construct reusable SparkSession factory, schema definitions, and I/O utilities.
- **Tasks:**
  - Implement `spark/utils/spark_session.py` with custom memory, cores, and serializer configs.
  - Implement `spark/utils/schemas.py` defining strict `StructType` schemas for all entities.
  - Implement `spark/utils/io_helpers.py` for reading/writing partitioned Parquet with Snappy.
  - Verify Spark Master/Executor connectivity in local or pseudo-distributed mode.
- **Expected Output:** Robust PySpark driver harness capable of loading datasets from HDFS/local storage.
- **Dependencies:** Phase 5.
- **Completion Criteria:** SparkSession successfully instantiates and loads raw datasets into Spark DataFrames.
- **Testing Requirements:** Test script asserting DataFrame row count matches raw generated data.

---

### Phase 7: Regional Trend & Geo-Spatial Analytics (Module 1)
- **Status:** **NOT STARTED**
- **Objective:** Implement distributed Spark SQL aggregations to identify hyper-local product trends.
- **Tasks:**
  - Implement `spark/analytics/regional_trends.py`.
  - Group events by `state`, `city`, `category`, and `event_type`.
  - Calculate top-N searched, viewed, carted, and purchased products per city using Spark Window functions (`dense_rank()`).
  - Export results to `/ecommerce/processed/regional_trends/` as partitioned Parquet.
- **Expected Output:** Partitioned Parquet dataset summarizing regional consumer demand and product rankings.
- **Dependencies:** Phase 6.
- **Completion Criteria:** Successful execution of Spark SQL aggregation jobs with correct ranking outputs.
- **Testing Requirements:** Unit test verifying rank calculation against a deterministic 1,000-row sample fixture.

---

### Phase 8: Multi-Action Demand Scoring Engine (Module 2)
- **Status:** **NOT STARTED**
- **Objective:** Compute normalized, weighted composite demand scores per product and region.
- **Tasks:**
  - Implement `spark/demand/demand_scorer.py`.
  - Aggregate funnel action counts ($C_{search}, C_{view}, C_{cart}, C_{purchase}$).
  - Normalize action frequencies per regional category partition.
  - Apply weighted scoring:
    $$\text{Demand Score} = 0.15 \cdot \tilde{S} + 0.20 \cdot \tilde{V} + 0.30 \cdot \tilde{C} + 0.35 \cdot \tilde{P}$$
  - Write output to `/ecommerce/processed/demand_scores/`.
- **Expected Output:** Normalized demand score DataFrame per product, city, and date.
- **Dependencies:** Phase 7.
- **Completion Criteria:** Demand scores bounded between 0.0 and 1.0 (or normalized benchmark scale).
- **Testing Requirements:** Mathematical assertion test verifying boundary limits and weighting integrity.

---

### Phase 9: Supply-Demand Mismatch Analysis (Module 3)
- **Status:** **NOT STARTED**
- **Objective:** Join demand scores with warehouse inventory snapshots to identify shortages and excess stock.
- **Tasks:**
  - Implement `spark/supply/mismatch_detector.py`.
  - Perform distributed join between `demand_scores` and `inventory` on `(product_id, city)`.
  - Calculate the Stock-to-Demand Ratio:
    $$SDR = \frac{\text{Available Stock}}{\text{Demand Score} \times K_{scale}}$$
  - Classify inventory states into `CRITICAL_SHORTAGE`, `BALANCED`, and `EXCESS_INVENTORY`.
  - Write output to `/ecommerce/processed/supply_demand/`.
- **Expected Output:** Partitioned Parquet table containing regional stock health and shortage risk classifications.
- **Dependencies:** Phase 8.
- **Completion Criteria:** Correct classification of high-demand/low-stock vs. low-demand/high-stock pairs.
- **Testing Requirements:** Test case asserting that products with zero inventory and positive demand receive `CRITICAL_SHORTAGE`.

---

### Phase 10: Multi-Granular Temporal Analytics (Module 4)
- **Status:** **NOT STARTED**
- **Objective:** Aggregate event traffic and conversions across hourly, daily, weekly, and monthly dimensions.
- **Tasks:**
  - Implement `spark/analytics/temporal_analytics.py`.
  - Extract temporal attributes (`hour`, `day_of_week`, `day_name`, `month`, `is_weekend`) from timestamps.
  - Compute hourly event velocity, peak purchasing windows, and conversion rates across categories.
  - Write output to `/ecommerce/processed/temporal/`.
- **Expected Output:** Parquet tables summarizing circadian and day-of-week shopping patterns.
- **Dependencies:** Phase 6.
- **Completion Criteria:** Valid temporal metrics produced for 24 hours of the day and 7 days of the week.
- **Testing Requirements:** Verify that sum of hourly event totals equals total raw events.

---

### Phase 11: Discount Banding & Response Analytics (Module 5)
- **Status:** **NOT STARTED**
- **Objective:** Analyze purchasing volume and revenue across discrete promotional discount brackets.
- **Tasks:**
  - Implement `spark/analytics/discount_analytics.py`.
  - Bucket discount percentages into intervals: `0% (Full Price)`, `1-10%`, `11-20%`, `21-35%`, `36-50%`, `>50%`.
  - Calculate gross conversion rate, total GMV, and units sold per discount band.
  - Write output to `/ecommerce/processed/discount/`.
- **Expected Output:** Aggregated metrics table correlating discount intensity with sales conversion.
- **Dependencies:** Phase 6.
- **Completion Criteria:** Complete aggregation table across all defined discount intervals.
- **Testing Requirements:** Verify that bracket allocations cover 100% of purchase events.

---

### Phase 12: Empirical Price Elasticity Modeling (Module 6)
- **Status:** **NOT STARTED**
- **Objective:** Compute empirical arc price elasticity of demand across categories and regional hubs.
- **Tasks:**
  - Implement `spark/pricing/price_elasticity.py`.
  - Formulate mid-point arc elasticity:
    $$E_d = \frac{(Q_2 - Q_1) / (Q_2 + Q_1)}{(P_2 - P_1) / (P_2 + P_1)}$$
  - Calculate category-level and regional price elasticity coefficients.
  - Classify product lines as `Elastic (|E| > 1)`, `Inelastic (|E| < 1)`, or `Unitary (|E| ≈ 1)`.
  - Write output to `/ecommerce/processed/elasticity/`.
- **Expected Output:** Category and regional price elasticity metric tables with outlier bounding.
- **Dependencies:** Phase 11.
- **Completion Criteria:** Econometrically bounded elasticity values calculated without division-by-zero crashes.
- **Testing Requirements:** Math assertion test validating arc formula computation on synthetic test points.

---

### Phase 13: Algorithmic Business Recommendation Engine (Module 7)
- **Status:** **NOT STARTED**
- **Objective:** Synthesize mismatch analytics and elasticity metrics into automated, vendor-facing recommendations.
- **Tasks:**
  - Implement `spark/pricing/recommendation_engine.py`.
  - Formulate deterministic business rules:
    - *Action 1 (Urgent Restock):* High demand + critical shortage.
    - *Action 2 (Promotional Liquidation):* Excess inventory + elastic demand $\rightarrow$ apply targeted discount.
    - *Action 3 (Margin Recovery):* Inelastic demand + high discount $\rightarrow$ reduce discount depth.
    - *Action 4 (Inter-Hub Transfer):* City A deficit + City B surplus for the same product $\rightarrow$ rebalance inventory.
  - Output structured recommendation records with quantitative justifications.
  - Write output to `/ecommerce/processed/recommendations/`.
- **Expected Output:** Final vendor recommendation dataset containing actionable, compute-grounded guidance.
- **Dependencies:** Phase 9, Phase 12.
- **Completion Criteria:** All generated recommendations contain concrete numerical evidence from underlying DataFrames.
- **Testing Requirements:** Test that recommendations trigger accurately for simulated edge-case records.

---

### Phase 14: Interactive Streamlit + Plotly Dashboard
- **Status:** **NOT STARTED**
- **Objective:** Construct the academic vendor analytics dashboard using Streamlit and Plotly.
- **Tasks:**
  - Implement `dashboard/components/data_loader.py` with `@st.cache_data` reading processed Parquet tables.
  - Implement `dashboard/components/sidebar.py` containing unified filters (Date, Region, City, Category, Discount).
  - Implement `dashboard/components/kpi_cards.py` displaying core business metrics.
  - Build visualization tabs:
    - Geo-Spatial Map (`dashboard/charts/geo_map.py`) using Plotly OpenStreetMap.
    - Demand & Funnel Visuals (`dashboard/charts/demand_charts.py`).
    - Supply-Demand Scatter (`dashboard/charts/mismatch_charts.py`).
    - Temporal Trends (`dashboard/charts/temporal_charts.py`).
    - Elasticity Curves (`dashboard/charts/elasticity_charts.py`).
    - Vendor Recommendations View (`dashboard/components/recommendations_view.py`).
  - Assemble main entry point `dashboard/app.py`.
- **Expected Output:** Interactive web application serving responsive analytics on `http://localhost:8501`.
- **Dependencies:** Phase 13.
- **Completion Criteria:** Dashboard loads cleanly in browser with functional interactive filters.
- **Testing Requirements:** Smoke test verifying all tabs render without errors on sample processed data.

---

### Phase 15: End-to-End Pipeline Integration Testing
- **Status:** **NOT STARTED**
- **Objective:** Validate end-to-end execution from raw data generation to final dashboard rendering.
- **Tasks:**
  - Build master orchestration script `scripts/run_pipeline.py`.
  - Execute full sequence: Generation $\rightarrow$ Validation $\rightarrow$ HDFS Ingestion $\rightarrow$ Spark Jobs $\rightarrow$ Dashboard Serving.
  - Verify data consistency across intermediate stages.
  - Ensure zero manual intervention required for pipeline completion.
- **Expected Output:** Fully automated execution pipeline with detailed operational logs.
- **Dependencies:** Phase 14.
- **Completion Criteria:** `python scripts/run_pipeline.py --scale demo` completes successfully.
- **Testing Requirements:** Complete end-to-end integration test executed via CLI.

---

### Phase 16: Performance & Scalability Benchmarking
- **Status:** **NOT STARTED**
- **Objective:** Profile Spark job performance, execution times, and memory efficiency across varying dataset scales.
- **Tasks:**
  - Run pipeline at 100k, 1M, and 5M+ event scales.
  - Capture Spark job execution times, stage durations, and memory consumption.
  - Profile impact of Broadcast Hash Joins vs. Shuffle Hash Joins.
  - Generate scalability comparison tables and charts for viva presentation.
- **Expected Output:** Benchmarking report with empirical execution metrics and Spark DAG analysis.
- **Dependencies:** Phase 15.
- **Completion Criteria:** Documented runtime metrics for multiple dataset scales.
- **Testing Requirements:** Automated benchmark execution script recording timestamps and system resource utilization.

---

### Phase 17: Viva Visual Documentation & Screenshots
- **Status:** **NOT STARTED**
- **Objective:** Capture high-resolution visual evidence of dashboard views, terminal logs, and architecture diagrams.
- **Tasks:**
  - Capture dashboard screenshots across all 6 analytical views.
  - Capture terminal outputs of HDFS commands (`hdfs dfs -ls /ecommerce/`).
  - Capture Spark Web UI DAG execution visualizations.
  - Package screenshots and execution logs into `docs/screenshots/` and project report.
- **Expected Output:** Comprehensive visual portfolio ready for project evaluation and submission.
- **Dependencies:** Phase 16.
- **Completion Criteria:** All primary dashboard views, terminal runs, and Spark DAGs visually documented.
- **Testing Requirements:** Image file inspection for clarity and resolution.

---

### Phase 18: Final Presentation & Viva Voce Defense
- **Status:** **NOT STARTED**
- **Objective:** Prepare presentation slides, live demo scripts, and student oral defense notes.
- **Tasks:**
  - Prepare slide deck covering: Problem, Big Data Architecture, HDFS/Spark Justification, Algorithms, and Dashboard.
  - Script a 10-minute live demonstration flow highlighting team division of responsibilities.
  - Formulate standard viva Q&A answers (e.g., Why Spark instead of MapReduce? Why Parquet? How is price elasticity approximated?).
- **Expected Output:** Complete presentation deck, live demo script, and prepared oral defense.
- **Dependencies:** Phase 17.
- **Completion Criteria:** Rehearsed live demonstration executed within designated academic presentation time limit.
- **Testing Requirements:** Dry-run demonstration test on clean hardware.
