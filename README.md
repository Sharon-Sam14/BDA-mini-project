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
