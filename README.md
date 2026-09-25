# Geo-Spatial E-Commerce Analytics: Scalable Location-Aware Trend Detection and Discount Optimization Using Apache Spark

An academic Big Data Analytics (BDA) mini-project demonstrating distributed storage, distributed computing, and data visualization using free and open-source technologies.

---

## 🏛️ Architecture Overview

```
Python 3.10+ / Faker / NumPy
             ↓
Synthetic E-Commerce Event Generation
             ↓
Apache Hadoop HDFS (Distributed Block Storage)
             ↓
Apache Spark / PySpark / Spark SQL (Distributed Processing & Analytics)
             ↓
Aggregated Columnar Metrics (Apache Parquet with Snappy)
             ↓
Streamlit + Plotly Dashboard (Visual Exploration & Geo-Spatial Mapping)
```

---

## 📚 Project Documentation (Permanent Sources of Truth)

All project specifications are cataloged in the [`docs/`](docs/) directory:

1. **[docs/PRD.md](docs/PRD.md)**: Product Requirements Document (Problem statement, objectives, functional & non-functional requirements, schemas, rubric).
2. **[docs/Architecture.md](docs/Architecture.md)**: Technical Architecture (Mermaid diagrams, HDFS topology, PySpark processing, data flow, directory layout).
3. **[docs/Rules.md](docs/Rules.md)**: Project Rules & Standards (FOSS mandate, code conventions, zero-hallucination policy, Spark performance rules).
4. **[docs/Phases.md](docs/Phases.md)**: Project Execution Roadmap (19 discrete phases with completion and testing criteria).
5. **[docs/Design.md](docs/Design.md)**: UI/UX Design System (Color tokens, typography, chart standards, and 6-tab Streamlit dashboard layout).
6. **[docs/Memory.md](docs/Memory.md)**: Persistent Project Memory (Status log, mathematical formulas, decision records, assumptions).

---

## 👥 Team Responsibilities

- **Team Member 1:** Data Engineering & HDFS (Synthetic data generation, schema validation, HDFS ingestion).
- **Team Member 2:** Big Data Processing & Spark (PySpark pipeline, demand scoring, supply-demand mismatch, temporal analysis).
- **Team Member 3:** Business Analytics & Visualization (Discount elasticity modeling, recommendation engine, Streamlit + Plotly dashboard).


## 🛠️ Onboarding & Local Environment Setup

Follow these steps sequentially to configure your local development workspace and sync system environment parameters.

### 1. Machine Prerequisites
Install these system-wide environments globally before initializing the repository:
- **Python 3.11** (Ensure the installer checkbox **"Add python.exe to PATH"** is selected)
- **Eclipse Temurin JDK 17** (Ensure **"Set JAVA_HOME variable"** is enabled during the install wizard)

### 2. Hadoop Storage Drivers (Windows Requirement)
Because Apache Spark relies on POSIX-like system configurations to interact with local storage networks on Windows:
1. Create a local folder structure explicitly mapped to: `C:\hadoop\bin\`
2. Place the Hadoop 3.x `winutils.exe` application binary file directly inside that `bin` folder.
   *(Final verification path footprint must read: `C:\hadoop\bin\winutils.exe`)*

### 3. Virtual Workspace Initialization
Open your Command Prompt (cmd) inside the root directory `D:\AOA\BDA-mini-project-main` and isolate the dependency layers:

```cmd
:: Create your isolated machine virtual environment configuration
py -3.11 -m venv venv

:: Activate the local virtual environment workspace
venv\Scripts\activate

:: Synchronize exact operational library footprints 
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Active System Path Mappings
Open the Windows Start menu, type **"Edit the system environment variables"**, open the dashboard tab, and add these parameters under **System Variables**:
- `JAVA_HOME` ➔ Path to your Eclipse Temurin installation folder (e.g., `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot`)
- `HADOOP_HOME` ➔ `C:\hadoop`

---

## 🧪 Pipeline Orchestration & Smoke Testing

To verify that your workspace runtimes, memory configurations, and Java hooks are communicating seamlessly, execute the master single-command automated pipeline:

```cmd
:: Re-activate your virtual runtime workspace environment
venv\Scripts\activate

:: Launch the end-to-end processing harness
python scripts/run_pipeline.py
```

### Ingestion Output Matrix
When executed cleanly, the automation loop will yield:
1. **`Phase 3`**: Generates 100,000 synthetic shopper logs (`data/raw/`).
2. **`Phase 4`**: Boots a local PySpark master node cluster to enforce geographic boundaries, schema casting, and catalog referential integrity rules.
3. **`Phase 5`**: Establishes local raw staging file paths and configures processing folders (`data/processed/`).

If your terminal window returns **`🎉 ALL INGESTION PIPELINE STAGES COMPLETED CLEANLY 🎉`**, your environment is completely configured!
