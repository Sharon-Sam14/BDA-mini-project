# Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark

## Chapter 1: Introduction

### 1.1 Description
This project focuses on resolving supply chain imbalances and evaluating localized customer interest patterns within modern e-commerce systems. Traditional platforms process data centrally, leading to computational bottlenecks and outdated localized inventory routing. This system processes high-velocity, multi-million record transactional log streams mapped to localized coordinates, extracting real-time insights to dynamically balance market variations.

### 1.2 Problem Formulation
E-commerce networks frequently encounter sudden local stock variations where a specific item is sold out in one warehouse zone but overstocked in another. Standard transactional pipelines fail to evaluate how early-stage user actions (like casual page clicks or cart additions) scale into definitive local demand metrics. The architectural problem requires executing low-latency distributed operations to scale multi-modal event parameters and identify supply-demand variance without exhausting server system memory.

### 1.3 Motivation
Modern big data infrastructures require fast, horizontal scale-out engines to translate high-velocity clickstreams into immediate operational steps. Building an optimized data pipeline via Apache Hadoop and PySpark illustrates how distributed computing frameworks handle large analytical workloads. This provides an effective model for understanding parallel data storage partitions, cluster transformations, and live spatial tracking modules.

### 1.4 Proposed Solution
The project implements a distributed analytical workflow to evaluate transactional data streams:
1. **Distributed Raw Data Storage:** Transaction logs and inventory tables containing over 5 million records are split into 128MB data blocks across Apache Hadoop HDFS DataNodes.
2. **Min-Max Feature Scaling:** PySpark standardizes highly variant data columns (such as high-volume page views and low-volume purchase transactions) onto an unbiased 0-to-1 range.
3. **Funnel-Weighted Priority Aggregations:** User actions are aggregated through a conditional scoring structure via PySpark `groupBy()` and `agg()` transformations to output a spatial Demand Matrix.
4. **Rule-Based Mismatch Analysis:** The Demand Matrix is joined with warehouse supply data to run a rule-based decision tree that automates stock alerts ("Critically Low", "Surplus") and local discount strategies.
5. **Presentation Layer:** The final analytical layers are loaded into an interactive Streamlit dashboard mapping dynamic local insights.

### 1.5 Scope of the Project
The primary scope is to validate a scalable batch and stream analytics engine that optimizes inventory tracking within specific geographic circles. The framework is restricted to processing spatial parameters (latitude/longitude metadata), transaction indicators, and structural warehouse volumes, serving as an automated back-end engine for real-time dynamic pricing.

---

## Chapter 2: Review of Literature
* **Distributed File Storage Architectures (HDFS):** Shvachko et al. discuss how splitting large transactional records into fixed data blocks across modular slave hardware preserves files from local hardware errors.
* **In-Memory Analytical Frameworks:** Zaharia et al. present the performance benefits of Apache Spark Dataframes, showcasing how utilizing Resilient Distributed Datasets (RDDs) and in-memory caching speeds up processing relative to legacy MapReduce disk writes.
* **Dynamic Resource Optimization Rules:** Standard rule-based decision trees provide deterministic logic execution when running multi-stage relational joins across vast datasets, allowing for rapid real-time calculations.

---

## Chapter 3: System Analysis

### 3.1 Functional Requirements
* **FR1:** The system must partition and store high-velocity transaction and inventory streams within the HDFS engine.
* **FR2:** The processing layer must execute a Min-Max calculation to normalize distinct metrics into a matching 0-to-1 scale.
* **FR3:** The pipeline must apply funnel weights to separate shopping intents and generate a consolidated Demand Matrix.
* **FR4:** The engine must execute an automated distributed join to compare the live local demand index against physical inventory limits.
* **FR5:** The frontend must read the final analytical tables to render geo-spatial status alerts on a visual interface.

### 3.2 Non-Functional Requirements
* **3.2.1 Performance Requirements:** Parallel processing loops must execute across all available CPU cores to handle 5+ million data rows without system execution failures.
* **3.2.2 Software Quality Attributes:** The pipeline must feature high fault tolerance via Spark's lazy evaluation maps, recalculating lost partitions automatically if a node disconnects.

### 3.3 Specific Requirements
* **Hardware Requirements:** Modern multi-core x86 CPU, 8GB+ System RAM, 20GB available Local Storage.
* **Software Requirements:** Windows OS / Linux environment, Python, Apache Hadoop (v3.x), Apache Spark / PySpark (v3.x), VS Code environment, Streamlit Web Library.

### 3.4 Use Case Diagram Description
* **Actors:** System Administrator (Data Engineer), Business Operations Manager.
* **Use Cases:** Upload Transaction Logs, Execute Scaling Engine, Generate Demand Matrix, View Geo-Spatial Mismatch Map, Adjust Discount Multipliers.

---

## Chapter 4: Analysis Modeling

### 4.1 Class Diagram and Activity Diagram Content
* **Data Flow Entities:** `RawLogsDataFrame`, `NormalizedTrendsDataFrame`, `DemandMatrixDataFrame`, `InventoryDataFrame`, `MismatchAlertsDataFrame`.
* **Activity Sequences:** Initial log intake -> PySpark distributed scaling -> Location grouping aggregation -> Warehouse dataframe join -> Decision tree validation -> File storage export to HDFS -> Streamlit dashboard render.

### 4.2 Functional Modeling (Data Flow)
* **DFD Level 0:** Raw Logs & Supply Sheets -> [Geo-Spatial Analytics Core Engine] -> Streamlit Live Visual Maps.
* **DFD Level 1:** Raw Files -> (1.1 HDFS Block Storage) -> (1.2 Min-Max Preprocessing) -> (1.3 GroupBy Funnel Aggregator) -> (1.4 Mismatch Decision Tree Engine) -> Processed Output Parquet Files.

---

## Chapter 5: Design

### 5.1 Architectural Design
The architecture follows a strict 3-tier decoupling framework:
1. **Storage Tier:** Apache Hadoop HDFS running a master-slave configuration (`NameNode` tracks system paths/metadata blocks; `DataNodes` physically store raw chunk files).
2. **Processing Tier:** PySpark engine utilizing horizontal partitioning structures, lazy evaluation mappings, and in-memory data tables.
3. **User Presentation Tier:** Streamlit web application running Plotly graphing logic for local monitoring.

### 5.2 User Interface Design
* **Control Panels:** File ingestion trigger paths, adjustable discount coefficient sliders, regional filter checkboxes.
* **Visual Outputs:** Interactive coordinate scatter maps (color-coded by mismatch status), distribution metrics bars, inventory alert notifications.

---

## Chapter 6: Implementation

### 6.1 Algorithms

#### Algorithm 1: Min-Max Feature Scaling
Converts raw, unaligned metrics into an equivalent 0-to-1 range using the absolute minimum and maximum parameters within that metric profile:
\[x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}\]

#### Algorithm 2: Funnel-Weighted Priority Scoring
Processes multi-stage click logs, transforming distinct interaction types via set operational multipliers:
\[\text{Demand Score} = \sum (\text{Views} \times 0.1) + (\text{Cart Additions} \times 0.5) + (\text{Stockouts} \times 1.0)\]

#### Algorithm 3: Rule-Based Supply Mismatch Decision Tree
Categorizes regional inventory stability states by routing combined parameters through distinct logic branches:
* **IF** \(\text{Demand Index} \ge 0.8\) AND \(\text{Inventory Stock} \le 10 \rightarrow\) State: `"Critically Understocked"` (Scale down local discount rate).
* **IF** \(\text{Demand Index} \le 0.3\) AND \(\text{Inventory Stock} \ge 100 \rightarrow\) State: `"Overstocked / Surplus"` (Boost local discount rate).

### 6.2 Working of the Project
* **Phase 1:** Synthetic customer logs are streamed into HDFS. The PySpark script communicates with the NameNode to locate the data targets.
* **Phase 2:** The pipeline pulls data blocks into system RAM, executing parallel calculations to isolate global boundaries and run Min-Max transformations.
* **Phase 3:** The engine aggregates rows by latitude and longitude coordinates using `.groupBy()`, generating the weighted spatial Demand Matrix.
* **Phase 4:** The framework runs a distributed inner join to match regional demand with warehouse inventory files, feeding the combined tables into conditional structures to trigger optimization alerts.
* **Phase 5:** Output results are saved as structured Parquet files back to HDFS. The Streamlit script reads these records to build operational metric screens.

---

## Chapter 7: Conclusions
This architecture highlights how distributed computation engines convert high-velocity log networks into active distribution steps. By combining Apache Hadoop storage maps with PySpark’s analytical layer, the platform handles complex calculations across massive data matrices without straining localized system memory. Future upgrades include migrating the file infrastructure into a live messaging channel like Apache Kafka for continuous stream transformations.
