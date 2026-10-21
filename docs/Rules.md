# Project Rules & Engineering Standards

**Project Title:** Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark  
**Academic Context:** Big Data Analytics (BDA) Academic Mini-Project  
**Document Version:** 1.0.0  
**Status:** Permanent Source of Truth & Enforcement Policy  

---

## 1. General Project Principles

1. **Scope Integrity:** Never expand, alter, or reduce the approved project scope without explicit review. All features must map directly to [PRD.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/PRD.md).
2. **Zero-Cost / Open-Source Mandate:** Only 100% free and open-source software (FOSS) is permitted. Never introduce paid APIs, cloud services (AWS, Azure, GCP), proprietary SDKs, or trial-license software.
3. **No Unnecessary Technologies:** Do not add complex frameworks (e.g., Kafka, Kubernetes, Cassandra, Redis, MongoDB, Elasticsearch, GraphQL) unless an explicit requirement warrants them. The core stack remains: Python, Faker, HDFS, Apache Spark (PySpark), Streamlit, and Plotly.
4. **Academic Authenticity & Rigor:** This is an academic engineering project. Never fabricate analytical metrics, processing times, or scalability numbers. Every output presented must be computationally verifiable.
5. **Clean Team Boundaries:** Team members must write code conforming to modular package interfaces so integration remains seamless and conflict-free.

---

## 2. Code Quality & Software Engineering Rules

1. **PEP 8 Compliance:** All Python source code must follow PEP 8 style conventions (4-space indentation, snake_case functions/variables, PascalCase classes, UPPER_CASE constants).
2. **Type Annotations & Documentation:** All public functions, methods, and classes must include Python 3 type hints (`typing`) and comprehensive docstrings detailing inputs, outputs, and edge cases.
3. **Modular Design & DRY (Don't Repeat Yourself):**
   - Business logic must reside in reusable modules inside `/spark/`, `/scripts/`, or `/dashboard/`.
   - Never duplicate data transformation logic across notebooks and production scripts.
4. **Configuration Isolation:**
   - Hardcoded constants (file paths, cluster URLs, port numbers, mathematical weights) inside Python source files are strictly prohibited.
   - All operational settings must reside in configuration files (`config/pipeline_config.yaml` or `config/spark_config.yaml`).
5. **Clean Dependency Management:**
   - All external packages must be pinned with explicit versions in `requirements.txt`.
   - Avoid bloated or redundant libraries.

---

## 3. Data Integrity & Zero-Hallucination Policy

1. **Strict Schema Adherence:** Synthetic data generators must strictly output datasets complying with the schemas specified in [PRD.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/PRD.md) and [Architecture.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Architecture.md).
2. **Deterministic Seed Control:** All synthetic data generation scripts must accept a random seed parameter (`--seed 42`) to guarantee reproducible datasets across machines.
3. **Validation & Anomaly Detection:**
   - Every generated batch must pass automated validation before ingestion (null check, coordinate bounds, positive price verification).
   - Incomplete or malformed records must be routed to a designated quarantine path or logged.
4. **Labeling Incomplete Information:**
   - If a metric has not yet been computed, it must be explicitly labeled: `NOT YET CALCULATED`.
   - If an architectural choice requires confirmation, label it: `DECISION REQUIRED`.
   - If an assumption is made regarding data behavior or business logic, explicitly tag it: `ASSUMPTION`.

---

## 4. Big Data & Apache Spark Processing Rules

1. **No Full In-Memory Pandas Processing:** Never load multi-million record datasets directly into a standard Pandas DataFrame. Raw and multi-row transformations must execute inside PySpark.
2. **Strict Ban on Unbounded `collect()`:**
   - Never execute `.collect()` or `.toPandas()` on large, unaggregated Spark DataFrames.
   - Only call `.collect()`, `.first()`, or `.take(n)` on small, aggregated metric summaries.
3. **Columnar Parquet Standard:**
   - Stored intermediate and processed analytical outputs must use Apache Parquet with Snappy compression.
   - Raw CSVs are permitted solely as ingestion staging fixtures.
4. **Optimized Join Strategies:**
   - When joining the large `events` DataFrame with the small `products` catalog dimension (~5,000 rows), always use a Broadcast Hash Join (`pyspark.sql.functions.broadcast`).
5. **Partitioning & Pruning:**
   - Raw event tables must be partitioned by logical temporal dimensions (e.g., `date=YYYY-MM-DD`).
   - Query filters must leverage partition keys to enable partition pruning and minimize disk I/O.
6. **Lazy Evaluation Discipline:** Understand Spark's transformation vs. action model. Avoid executing unnecessary terminal actions (`count()`, `show()`) inside production loops.
7. **Cache & Persist Wisely:** Only use `.persist(StorageLevel.MEMORY_AND_DISK)` on DataFrames that are evaluated multiple times across distinct downstream branches. Always invoke `.unpersist()` when processing finishes.

---

## 5. Hadoop HDFS Operational Rules

1. **Separation of Raw and Processed Zones:**
   - `/ecommerce/raw/` is write-once, read-many (immutable). Never modify raw ingestion files in place.
   - `/ecommerce/processed/` contains aggregated, partitioned analytics ready for serving.
2. **Deterministic HDFS Directory Conventions:** All HDFS paths must follow the documented structure:
   - Events: `/ecommerce/raw/events/`
   - Products: `/ecommerce/raw/products/`
   - Inventory: `/ecommerce/raw/inventory/`
   - Analytics: `/ecommerce/processed/<module_name>/`
3. **Resilient Local Fallback:**
   - For environments where an active Hadoop cluster is unavailable or during early development, the pipeline must support a seamless local filesystem fallback (`./data/raw/` and `./data/processed/`) controlled by a single configuration toggle (`storage.type: hdfs | local`).

---

## 6. Business Analytics & Formulation Rules

1. **Documented Mathematical Formulas:**
   - Every metric (Demand Score, Stock-to-Demand Ratio, Price Elasticity) must have its exact mathematical equation documented in [Architecture.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Architecture.md) and [Memory.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Memory.md).
2. **Zero Hardcoded Recommendations:**
   - Recommendation alerts (e.g., "Restock Mumbai Warehouse for Product X") must be dynamically generated from computed metrics and threshold evaluations.
   - Never hardcode static strings as recommendation outputs.
3. **Causation vs. Correlation:**
   - Analytical observations must be framed scientifically. Do not assert absolute causal pricing behavior when presenting empirical correlation or arc elasticity approximations.
4. **Safe Division & Boundary Clamping:**
   - Always guard against division by zero in price changes ($\Delta P = 0$) or zero inventory.
   - Clamp unbounded elasticity outliers to mathematically interpretable intervals.

---

## 7. Dashboard & UI Design Rules

1. **Data-Centric Visual Focus:**
   - The Streamlit interface must be clean, academic, modern, and professional.
   - Strictly prohibit gaming aesthetics, neon glow effects, excessive glassmorphism, or gratuitous CSS animations.
2. **Pre-Aggregated Serving Only:**
   - The dashboard must **never** trigger heavy Spark jobs or parse millions of raw events on page reload.
   - It must read pre-aggregated, compact Parquet files into memory using `@st.cache_data`.
3. **Universal Responsiveness:**
   - Visualizations must resize responsively and handle filter combinations gracefully (displaying clear empty-state messages when a filter yields no matching records).
4. **Contextual Clarity:**
   - Every chart, scorecard, and table must feature descriptive titles, labeled axes, units of measurement (e.g., INR ₹, units, %), and informational tooltips.

---

## 8. AI Assistant & Coding Agent Operational Rules

1. **Inspect Before Modifying:** Always inspect and read existing files and directory structures before creating or modifying code.
2. **Never Overwrite Blindly:** When modifying existing codebase files, verify surrounding context and preserve unrelated existing code and comments.
3. **No Phantom Requirements:** Do not invent features, microservices, cloud dependencies, or database engines that are not explicitly documented in [PRD.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/PRD.md).
4. **Precedence Hierarchy:** If an ambiguity or conflict arises, the authoritative hierarchy of truth is:
   1. User's explicit prompt instructions
   2. [Rules.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Rules.md)
   3. [PRD.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/PRD.md)
   4. [Architecture.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Architecture.md)
   5. [Phases.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Phases.md)
5. **State Synchronization:** Always update [Memory.md](file:///c:/Users/sharo/Desktop/BDA%20MINI/docs/Memory.md) upon completing any phase, architectural milestone, or major debugging resolution.

---

## 9. Testing & Validation Rules

1. **Unit Testing:** Core mathematical calculations (Demand Score, Arc Elasticity, Stock Ratios) must have automated unit tests in `/tests/` with known expected values.
2. **Schema Verification:** Automated tests must verify that generated synthetic data contains zero schema mismatches and no unexpected nulls in primary key columns.
3. **Dashboard Smoke Tests:** Verify that all dashboard tabs load without throwing runtime exceptions when reading sample datasets.
4. **Test Independence:** Tests must run autonomously without requiring active external internet access or external cloud services.
