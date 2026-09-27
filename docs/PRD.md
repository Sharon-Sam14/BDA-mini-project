# Project Requirements Document (PRD)

**Project Title:** Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark  
**Academic Context:** Big Data Analytics (BDA) Academic Mini-Project  
**Document Version:** 1.0.0  
**Status:** Approved Baseline  
**Target Environment:** Local Distributed Mode (HDFS + Apache Spark / PySpark on Ubuntu/Linux or Windows WSL2)  

---

## 1. Executive Summary & Overview

Modern e-commerce enterprises generate massive volumes of continuous event streams—ranging from initial search queries and product detail views to cart additions and completed checkout transactions. Standard relational database systems and single-node data processing tools (e.g., standalone Pandas) fail to scale efficiently when analyzing multi-million event datasets across geographical and temporal dimensions.

This project implements an end-to-end Big Data Analytics (BDA) pipeline using **Apache Hadoop HDFS** for distributed storage, **Apache Spark (PySpark & Spark SQL)** for distributed batch processing and analytics, and an interactive **Streamlit + Plotly** dashboard for vendor-oriented visual exploration. The system analyzes high-volume synthetic clickstream and inventory data to uncover hyper-local product trends, regional supply-demand mismatches, temporal demand fluctuations, and discount price elasticity.

---

## 2. Problem Statement & Motivation

### 2.1 Problem Statement
E-commerce merchants frequently struggle with two interconnected challenges:
1. **Geographic Supply-Demand Imbalance:** Inability to detect regional demand surges in real-time, resulting in localized stockouts in high-demand cities while identical products sit idle as excess inventory in neighboring regions.
2. **Suboptimal Discounting Strategies:** Applying uniform discount percentages nationwide without accounting for regional consumer price sensitivity, category demand elasticity, and inventory pressure.

### 2.2 Academic Motivation
This project serves as an applied academic demonstration of core Big Data concepts:
- **Distributed File Systems (HDFS):** Managing scalable, fault-tolerant block storage for raw clickstream logs and columnar processed datasets.
- **Distributed In-Memory Processing (Apache Spark):** Leveraging Resilient Distributed Datasets (RDD abstractions), DataFrames, Spark SQL Catalyst optimization, distributed aggregations, windowing functions, and join strategies.
- **Data Engineering Best Practices:** Schema enforcement, partition pruning, columnar storage (Parquet with Snappy compression), and avoiding driver bottlenecks (e.g., preventing unbounded `collect()` calls).
- **Applied Business Analytics:** Formulating mathematically sound demand scoring, supply-demand mismatch indexing, and empirical discount price elasticity approximations.

---

## 3. Target Users & Stakeholders

| User Role | Needs & Objectives | Interaction with System |
| :--- | :--- | :--- |
| **Vendor / Merchant** | Identify localized product demand, adjust regional stock allocation, optimize promotional discount depths. | Interacts with Streamlit dashboard filter panels and recommendation views. |
| **Inventory / Supply Chain Manager** | Detect stockout vulnerabilities and regional surplus to orchestrate inter-hub inventory rebalancing. | Analyzes supply-demand mismatch maps, stock-to-demand ratios, and shortage alerts. |
| **Pricing / Marketing Analyst** | Understand customer price sensitivity by category and region; evaluate promotional effectiveness. | Inspects discount-demand curves and empirical price elasticity metrics. |
| **Academic Evaluator / Faculty** | Verify architectural soundness, Spark execution efficiency, distributed principles, and analytical validity. | Reviews code modularity, HDFS/Spark execution plans (`explain()`), scalability logs, and viva demonstration. |

---

## 4. Scope & Boundaries

### 4.1 In Scope
- **Data Generation:** Synthetic generation of scalable, realistic e-commerce events (100,000+ users, 5,000+ products, 1M–10M+ events, 100,000+ inventory entries) with controlled geographic and temporal distributions.
- **Storage Layer:** Distributed raw and processed storage on Apache Hadoop HDFS (with local filesystem fallback for development).
- **Batch Processing Layer:** Scalable PySpark and Spark SQL pipeline handling data cleansing, schema casting, temporal extraction, distributed joins, and complex aggregations.
- **Analytics Engine:**
  - Regional / geo-spatial trend detection (searches, views, carts, purchases by city/state).
  - Multi-action normalized demand scoring.
  - Regional supply-demand mismatch detection.
  - Multi-granular temporal pattern analysis (hourly, daily, weekly, monthly).
  - Discount-price relationship and empirical price elasticity calculation.
  - Rule-based, compute-derived vendor recommendations.
- **Serving & Visualization:** Interactive, lightweight Streamlit dashboard featuring Plotly geographic maps, KPI scorecards, trend charts, and exportable business recommendations.
- **Verification & Benchmarking:** Performance and scalability profiling comparing Spark execution across varying dataset sizes.

### 4.2 Out of Scope
- Real-time stream processing with Apache Kafka or Spark Structured Streaming (batch execution is selected for architectural focus).
- Live transactional database integration (PostgreSQL, MongoDB, Cassandra, Redis).
- Production cloud deployment (AWS EMR, Google Cloud Dataproc, Azure Synapse).
- Black-box deep learning or predictive neural network pricing models (analytical/econometric approximations are preferred for interpretability).
- User authentication, multi-tenant billing, and web-scale frontend commerce storefronts.

---

## 5. Functional Requirements (FR)

Requirements are categorized into **MUST-HAVE (M)** and **OPTIONAL / ENHANCEMENT (O)**.

### 5.1 Module 0: Synthetic Data Generation & Ingestion
- **FR-01 (M):** System MUST generate synthetic data for three relational entities: `events`, `products`, and `inventory`.
- **FR-02 (M):** Data generation MUST utilize realistic Indian/global geographic coordinates (city, state, latitude, longitude) and realistic pricing/discount distributions.
- **FR-03 (M):** System MUST support generating configurable dataset profiles:
  - *Dev / Test Mode:* ~100k events for rapid iteration and unit testing.
  - *Demonstration Mode:* 1M–5M events for standard academic evaluation.
  - *Benchmark Mode:* 10M+ events for Spark distributed performance benchmarking.
- **FR-04 (M):** System MUST ingest raw data into HDFS under structured namespaces (`/ecommerce/raw/events/`, `/ecommerce/raw/products/`, `/ecommerce/raw/inventory/`).

### 5.2 Module 1: Regional & Geo-Spatial Trend Detection
- **FR-05 (M):** PySpark pipeline MUST compute top-N searched, viewed, cart-added, and purchased products per city and state.
- **FR-06 (M):** Pipeline MUST compute top product categories per region by transaction volume and gross merchandise value (GMV).
- **FR-07 (M):** Output MUST include aggregated location metrics (latitude, longitude, total events, total revenue) for map rendering.

### 5.3 Module 2: Demand Scoring Engine
- **FR-08 (M):** Pipeline MUST calculate a composite `Demand Score` per product per region over discrete time windows.
- **FR-09 (M):** Formula MUST incorporate weighted contributions across the consumer funnel: Searches ($w_1$), Views ($w_2$), Cart Additions ($w_3$), and Purchases ($w_4$), where weights sum to 1.0.
- **FR-10 (M):** Metric inputs MUST be normalized (min-max or regional scale) to prevent high-frequency events (views) from drowning low-frequency conversion events (purchases).

### 5.4 Module 3: Supply-Demand Mismatch Analysis
- **FR-11 (M):** Pipeline MUST execute a distributed join between aggregated regional demand and current available inventory.
- **FR-12 (M):** System MUST compute a `Stock-to-Demand Ratio` ($SDR$) and categorize inventory states:
  - *Critical Shortage / Stockout Risk:* High Demand, Low Inventory ($SDR < \theta_{low}$).
  - *Balanced:* Demand aligned with inventory buffer.
  - *Excess Inventory / Capital Lockup:* Low Demand, High Inventory ($SDR > \theta_{high}$).
- **FR-13 (M):** Pipeline MUST output top deficit and top surplus product-region pairs.

### 5.5 Module 4: Temporal Trend Analytics
- **FR-14 (M):** Pipeline MUST extract and aggregate event metrics across multiple temporal dimensions:
  - Hour-of-day (circadian shopping patterns).
  - Day-of-week (weekday vs. weekend conversion spikes).
  - Weekly / Monthly trends (longitudinal shifts).
- **FR-15 (M):** System MUST identify category-level peak purchasing hours across different urban regions.

### 5.6 Module 5: Discount & Pricing Analytics
- **FR-16 (M):** Pipeline MUST segment transactions into discrete discount bands (e.g., 0%, 1–10%, 11–20%, 21–35%, >35%).
- **FR-17 (M):** System MUST calculate sales volume, revenue, and average transaction quantity per discount bracket.
- **FR-18 (M):** Pipeline MUST categorize products into discount sensitivity tiers (High Sensitivity, Moderate Sensitivity, Inelastic/Low Sensitivity).

### 5.7 Module 6: Empirical Price Elasticity Approximation
- **FR-19 (M):** System MUST implement an academic point/arc price elasticity formula:
  $$\epsilon = \frac{\% \Delta Q}{\% \Delta P}$$
  where price variations reflect effective post-discount prices.
- **FR-20 (M):** Aggregation MUST group by product category and region to isolate contextual elasticity coefficients.
- **FR-21 (M):** Model MUST flag anomalies (e.g., positive elasticity indicative of Giffen goods or synthetic noise) and filter or bound estimates within economically plausible ranges.

### 5.8 Module 7: Actionable Business Recommendations
- **FR-22 (M):** Engine MUST generate rule-based recommendations derived strictly from computed analytical metrics:
  - *Restock Alerts:* Products with high demand score and low stock.
  - *Liquidation Alerts:* Products with excess inventory and low demand (recommend targeted discount).
  - *Discount Optimization Alerts:* Inelastic products with excessive discounts (recommend margin preservation).
- **FR-23 (M):** Recommendations MUST contain quantitative justification (e.g., "Current stock: 12 units; Estimated 7-day demand: 180 units").

### 5.9 Module 8: Interactive Dashboard & Visualizations
- **FR-24 (M):** Dashboard MUST be built using Streamlit and Plotly.
- **FR-25 (M):** System MUST render:
  - Executive KPI scorecards (Total Events, Total GMV, Active Regions, Top Product, Top City).
  - Interactive Plotly geographic scatter/bubble maps displaying demand hotspots.
  - Bar/Line charts for temporal shopping patterns and category distributions.
  - Scatter plots and regression trendlines for discount vs. quantity sold.
  - Supply-Demand risk quadrant scatter plots (Demand vs. Stock).
  - Filterable recommendations data table with CSV export.
- **FR-26 (O):** Choropleth geo-visualization shaded by state-level demand index.
- **FR-27 (O):** Automated PDF/HTML summary report generation.

---

## 6. Non-Functional Requirements (NFR)

### 6.1 Performance & Scalability
- **NFR-01:** Batch PySpark processing of 5,000,000 records MUST execute in under 3 minutes on standard student hardware (4 CPU cores, 8GB-16GB RAM allocation).
- **NFR-02:** Spark job execution MUST avoid memory overflow (`OutOfMemoryError: Java heap space`) by avoiding non-partitioned full shuffles and unbounded `collect()` operations.
- **NFR-03:** The Streamlit dashboard MUST load pre-aggregated Parquet summaries instantaneously (< 2.0 seconds initial load time).

### 6.2 Data Integrity & Governance
- **NFR-04:** Raw data ingested into HDFS MUST be treated as immutable (Write Once, Read Many - WORM principle).
- **NFR-05:** Processed datasets MUST be stored in columnar Apache Parquet format with snappy compression to reduce I/O footprint by at least 60% compared to raw CSV.
- **NFR-06:** Schema consistency MUST be validated during Spark ingestion; records failing schema constraints MUST be counted and quarantined.

### 6.3 Maintainability & Code Quality
- **NFR-07:** Python code MUST adhere strictly to PEP 8 standards with descriptive variable naming, static type hints, and modular package separation.
- **NFR-08:** Configuration parameters (paths, thresholds, weights, ports) MUST reside in centralized config files (`config.yaml` or `.py`), separate from business logic.

### 6.4 Usability & Academic Demonstrability
- **NFR-09:** The dashboard layout MUST be self-explanatory for academic reviewers, featuring labeled metrics, contextual tooltips, and clear mathematical definitions.
- **NFR-10:** Complete pipeline execution (Data Gen $\rightarrow$ HDFS Ingestion $\rightarrow$ Spark Processing $\rightarrow$ Dashboard Launch) MUST be triggerable via documented shell scripts or terminal commands.

---

## 7. Dataset Specifications

### 7.1 Entity Schemas

#### 1. `events` (Clickstream & Transactions)
| Field Name | Data Type | Description | Constraints / Examples |
| :--- | :--- | :--- | :--- |
| `event_id` | String / UUID | Unique event identifier | Primary Key |
| `user_id` | String | Unique customer identifier | e.g., `USR_0001234` |
| `product_id` | String | Foreign key to product entity | e.g., `PRD_00045` |
| `timestamp` | Timestamp | Timestamp of event occurrence | ISO 8601 (`YYYY-MM-DD HH:MM:SS`) |
| `event_type` | String | Funnel activity category | `search`, `view`, `cart`, `purchase` |
| `city` | String | City where event originated | e.g., `Mumbai`, `Bengaluru`, `Delhi` |
| `state` | String | State / Province | e.g., `Maharashtra`, `Karnataka` |
| `latitude` | Double | Geo coordinate | Range: -90.0 to +90.0 |
| `longitude` | Double | Geo coordinate | Range: -180.0 to +180.0 |
| `price` | Double | Effective transaction / listing price | $> 0.0$ |
| `discount_percent` | Double | Promotional discount applied | Range: 0.0 to 70.0 |
| `quantity` | Integer | Units selected/purchased | 1 for views/searches; $\ge 1$ for carts/purchases |

#### 2. `products` (Product Catalog Dimension)
| Field Name | Data Type | Description | Constraints / Examples |
| :--- | :--- | :--- | :--- |
| `product_id` | String | Unique product identifier | Primary Key (`PRD_XXXXX`) |
| `product_name` | String | Descriptive product name | e.g., `Wireless Noise-Canceling Headphones` |
| `category` | String | Primary retail category | `Electronics`, `Apparel`, `Home`, `Beauty` |
| `base_price` | Double | Manufacturer suggested retail price | $> 0.0$ |

#### 3. `inventory` (Regional Warehouse Stock Snapshot)
| Field Name | Data Type | Description | Constraints / Examples |
| :--- | :--- | :--- | :--- |
| `product_id` | String | Foreign key to product entity | Composite Key (`product_id` + `city` + `date`) |
| `city` | String | Regional distribution hub / city | e.g., `Mumbai`, `Delhi` |
| `available_stock` | Integer | Physical stock on hand | $\ge 0$ |
| `date` | Date | Snapshot observation date | `YYYY-MM-DD` |

### 7.2 Scalability Target Benchmarks
- **Users:** 100,000+ distinct IDs
- **Products:** 5,000+ catalog entries across 8+ categories
- **Events:** 1,000,000 to 10,000,000 records
- **Inventory Entries:** 200,000+ warehouse snapshot records

---

## 8. Dashboard Requirements & Layout

The vendor dashboard serves as the analytical presentation layer, displaying pre-computed Spark outputs:

### 8.1 Layout Structure
1. **Sidebar Controls:**
   - Date range selector (Start date to End date).
   - Multi-select filters: State / Region, City, Category, Product.
   - Discount threshold slider (0% to 70%).
2. **Tab 1 — Executive Overview:**
   - Metric scorecards: Total Events, Total Conversions, GMV, Active Hubs, Top-Performing Category.
   - High-level funnel visualization (Search $\rightarrow$ View $\rightarrow$ Cart $\rightarrow$ Purchase).
3. **Tab 2 — Regional & Geo-Spatial Trends:**
   - Plotly bubble map showing city-wise demand intensity and purchase volume.
   - Regional category affinity matrix and ranking tables.
4. **Tab 3 — Demand & Temporal Analytics:**
   - Hourly activity heatmaps showing conversion peaks.
   - Day-of-week demand trends by product category.
5. **Tab 4 — Supply-Demand Imbalance:**
   - Risk quadrant chart: Demand Score vs. Available Stock.
   - Urgent deficit alerts and excess inventory liquidation lists.
6. **Tab 5 — Discount & Elasticity Optimization:**
   - Discount bracket revenue vs. volume comparative bar charts.
   - Empirical price elasticity distribution across categories.
7. **Tab 6 — Actionable Vendor Recommendations:**
   - Algorithmic recommendation cards with clear quantitative justifications.
   - CSV export for procurement and marketing teams.

---

## 9. Team Structure & Work Division

The project is structured for a 3-member engineering team with clear boundaries and clean interfaces:

```
┌─────────────────────────────────────────────────────────────┐
│                       TEAM DIVISION                         │
├──────────────────────────────┬──────────────────────────────┤
│ Team Member 1                │ Team Member 2                │
│ Data Engineering & HDFS      │ Big Data Processing & Spark  │
│ • Synthetic data generation  │ • PySpark pipeline setup     │
│ • Schema & validation        │ • Spark SQL transformations  │
│ • HDFS cluster integration   │ • Regional trend detection   │
│ • Storage layout & formats   │ • Demand scoring algorithm   │
│ • Ingestion scripts          │ • Supply-demand mismatch     │
│ • Parquet optimization       │ • Spark benchmarking/tuning  │
├──────────────────────────────┴──────────────────────────────┤
│ Team Member 3                                               │
│ Business Analytics & Visualization                          │
│ • Discount elasticity analysis                              │
│ • Recommendation engine heuristics                          │
│ • Streamlit dashboard development                           │
│ • Plotly interactive visualizations                         │
│ • User interface integration                                │
│ • Viva demo scripting & presentation                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Constraints & Open-Source Compliance

1. **Strict Zero-Cost Guarantee:** 100% of libraries, runtimes, and tools are free, open-source software (FOSS). No credit cards, trial tokens, or cloud billing accounts are permitted.
2. **Local Hardware Constraints:** All services (HDFS NameNode/DataNode, Spark Master/Worker, Streamlit server) must be capable of running concurrently on standard academic laptops (8GB–16GB RAM, 4–8 CPU cores).
3. **Reproducibility:** The environment must be fully reproducible via a unified `requirements.txt` and deterministic shell execution scripts.

---

## 11. Success Criteria & Evaluation Rubric

| Criterion | Success Threshold | Verification Method |
| :--- | :--- | :--- |
| **Data Generation Scale** | $\ge 1,000,000$ valid records generated without memory crash | Record count verification script; file size inspection |
| **HDFS Storage** | Data successfully stored and organized in HDFS namespaces | `hdfs dfs -ls /ecommerce/` terminal command output |
| **Spark Processing** | Pipeline executes end-to-end; outputs partitioned Parquet tables | Spark job logs, DAG execution plan inspection |
| **Analytical Correctness** | Formulas accurately computed; recommendations mathematically grounded | Unit test assertions on sample subsets |
| **Dashboard Response** | Visualizations render interactively without driver lag | Interactive testing across filters (< 2 sec response) |
| **Viva Readiness** | Comprehensive architectural explanation and live execution | End-to-end execution demonstration script |
