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

---

# Part 1: Fresh Laptop Setup Guide (For Team Member 3)

## 1. Core Software Installations

### A. Install Java Development Kit (JDK 11)

PySpark and Hadoop require **JDK 11** on Windows.

1. Download **Eclipse Adoptium Temurin OpenJDK 11** (MSI installer) for Windows x64.
2. Run the installer.
3. **Important during setup:** Select the option **"Set JAVA_HOME variable"** and choose **"Will be installed on local hard drive"**.
4. The installation path should ideally be:

   ```
   C:\Program Files\Eclipse Adoptium\jdk-11.x.x.x-hotspot\
   ```

### B. Install Python 3.10+

1. Download Python (**3.10 to 3.12**) from [python.org](https://www.python.org/).
2. Run the installer and check the box **"Add python.exe to PATH"** before clicking **Install**.

### C. Install Git

1. Download and install Git for Windows from [git-scm.com](https://git-scm.com/).
2. Use all default installer settings.

---

## 2. Hadoop Native Windows Binaries Setup

Apache Hadoop requires native Windows binaries (`winutils.exe` and `hadoop.dll`) to run HDFS on Windows.

1. Create a folder named `C:\hadoop`.
2. Extract the pre-configured **Apache Hadoop 3.3.6** binaries into `C:\hadoop` so that `C:\hadoop\bin` and `C:\hadoop\sbin` exist.
3. Download the matching `winutils.exe` and `hadoop.dll` for **Hadoop 3.3.6**, then:
   - Place `winutils.exe` into `C:\hadoop\bin\`
   - Copy `hadoop.dll` into **both** `C:\hadoop\bin\` and `C:\Windows\System32\`

---

## 3. System Environment Variables Setup

Search for **"Edit the system environment variables"** in the Windows Start Menu and click **Environment Variables**.

> **Note on short paths:** Both `Program Files` and `Eclipse Adoptium` contain spaces, which break Hadoop's scripts. Find the exact 8.3 short names by running this in `cmd`:
>
> ```cmd
> dir /x "C:\Program Files"
> ```
>
> Look for the short name next to `Eclipse Adoptium` (usually `ECLIPS~1`). The resulting path is typically `C:\Progra~1\ECLIPS~1\jdk-11.x.x.x-hotspot`.

**System Variables (bottom box):**

1. Click **New**:
   - **Variable name:** `JAVA_HOME`
   - **Variable value:** `C:\Progra~1\ECLIPS~1\jdk-11.x.x.x-hotspot`
2. Click **New**:
   - **Variable name:** `HADOOP_HOME`
   - **Variable value:** `C:\hadoop`
3. Edit the `Path` variable → Click **New** → Add these entries:
   - `%JAVA_HOME%\bin`
   - `%HADOOP_HOME%\bin`
   - `%HADOOP_HOME%\sbin`

---

## 4. Hadoop XML Configuration Files

All files below are in `C:\hadoop\etc\hadoop\`.

### Edit `hadoop-env.cmd`

Find `set JAVA_HOME=` and set it using the short path, **without quotes**:

```cmd
set JAVA_HOME=C:\Progra~1\ECLIPS~1\jdk-11.x.x.x-hotspot
```

### Edit `core-site.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```

### Edit `hdfs-site.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///C:/hadoop/data/dfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///C:/hadoop/data/dfs/datanode</value>
    </property>
</configuration>
```

---

## 5. Repository Setup & First-Time Execution

Open **Command Prompt (`cmd`) as Administrator**.

### Step 1: Clone the Repository

```cmd
git clone https://github.com/Sharon-Sam14/BDA-mini-project.git
cd BDA-mini-project
```

### Step 2: Set Up the Python Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Format the HDFS NameNode (First-Time Only)

```cmd
hdfs namenode -format
```

### Step 4: Start HDFS Services

```cmd
cd C:\hadoop\sbin
start-dfs.cmd
```

> ⚠️ **Keep the two popped-up NameNode and DataNode windows open in the background!**

### Step 5: Generate Data & Execute the PySpark Job

Return to your project directory terminal (with `venv` active):

```cmd
python scripts/data_generation/generate_all.py --scale demo

hdfs dfs -mkdir -p /ecommerce/raw/events
hdfs dfs -mkdir -p /ecommerce/raw/products
hdfs dfs -mkdir -p /ecommerce/raw/inventory
hdfs dfs -mkdir -p /ecommerce/processed

hdfs dfs -put -f data/raw/events/events.csv /ecommerce/raw/events/
hdfs dfs -put -f data/raw/products/products.csv /ecommerce/raw/products/
hdfs dfs -put -f data/raw/inventory/inventory.csv /ecommerce/raw/inventory/

python spark/processing/process_regional_trends.py
```