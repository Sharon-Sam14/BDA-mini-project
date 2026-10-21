# AGENTS.md

## What this repo is

Academic Big Data Analytics mini-project: synthetic e-commerce events → HDFS → Spark/PySpark → Parquet → (planned) Streamlit + Plotly dashboard. Windows-first dev environment (README documents a Win Hadoop 3.3.6 setup).

**Current state:** Phases 0–9 complete; ingestion + validation + Spark analytics (`spark/preprocessing/`, `analytics/`, `demand/`, `supply/`, runner `spark/run_spark_analytics.py`) + `tests/` (22 pytest tests) exist. Not yet built: `dashboard/`, `notebooks/`, `spark/pricing/`, `config/spark_config.yaml`. `docs/Memory.md` and `docs/Phases.md` were reconciled with code on 2026-09-29 (Phases 7–9 marked COMPLETED), but **still trust the code over the docs' status tables**, and update `docs/Memory.md` when you complete a phase.

## Running things (Windows)

All scripts use **cwd-relative paths** (`data/raw/...`, `config/pipeline_config.yaml`) — always run from the repo root, never from a subdirectory.

```powershell
venv\Scripts\activate
python scripts/run_pipeline.py                       # generate (scale=dev) -> validate -> stage; phases 3-5
python scripts/data_generation/generate_all.py --scale dev|demo|benchmark   # 100k / 1M / 10M rows
python spark/preprocessing/validate_records.py       # needs generated data/raw/
python spark/processing/process_regional_trends.py   # needs HDFS running + data uploaded
```

- HDFS prerequisite: `cd C:\hadoop\sbin && start-dfs.cmd` (leave NameNode/DataNode windows open); `stop-dfs.cmd` when done. HDFS is at `hdfs://localhost:9000`.
- `scripts/run_pipeline.py` does **not** start HDFS or run the Spark analytics. HDFS upload is real now: `hdfs/hdfs_upload.py` executes `hdfs dfs -mkdir`/`-put`/`-ls` when `storage.type: hdfs` and **exits 1 (NOT VERIFIED)** if the `hdfs` CLI is missing — never fake success. HDFS has never been exercised on this machine (no Hadoop install yet).
- Member 2 entry point: `python spark/run_spark_analytics.py` (clean → regional → Spark SQL → demand → mismatch → Parquet under `data/processed/`); ~57s on 1M rows.
- Tests: `python -m pytest tests/ -v` (~90s, needs no HDFS; `tests/conftest.py` sets `HADOOP_HOME=C:\hadoop`, `PYSPARK_PYTHON=python` — both also set as user env vars).
- Env vars required: `JAVA_HOME` (JDK 11, **8.3 short path with no spaces**, e.g. `C:\Progra~1\ECLIPS~1\jdk-11...`; spaces break Hadoop scripts), `HADOOP_HOME=C:\hadoop`, plus `%JAVA_HOME%\bin`, `%HADOOP_HOME%\bin`, `%HADOOP_HOME%\sbin` on Path. `hadoop.dll` must be in `C:\hadoop\bin` **and** `C:\Windows\System32`.
- No lint/typecheck/CI exists. Tests exist (`tests/`, pytest): `python -m pytest tests/ -v` is the only test command; don't invent others.
- `requirements.txt` is saved as **UTF-16LE** — many tools see it as binary. Keep it pinned (Rules.md mandate); if you edit it, prefer re-saving as UTF-8 and verify `pip install -r requirements.txt` still parses.

## Sources of truth (precedence order)

1. Your explicit prompt instructions
2. `docs/Rules.md` — engineering rules & enforcement policy
3. `docs/PRD.md` — scope and requirements
4. `docs/Architecture.md` — planned directory tree and data flow
5. `docs/Phases.md` — 19-phase roadmap with per-phase completion/testing criteria

Also: `docs/Memory.md` (state log, formulas, decisions/assumptions), `docs/Design.md` (dashboard design system). README.md Part 1/2 is the authoritative environment-setup runbook.

## Hard constraints (docs/Rules.md — violating these breaks the project)

- **FOSS only.** No paid APIs, no AWS/Azure/GCP, no proprietary SDKs.
- **Fixed stack:** Python 3.10+, Faker, NumPy/Pandas, Hadoop HDFS 3.3+, PySpark, Parquet (Snappy), Streamlit, Plotly, pytest. Do not add Kafka/Redis/MongoDB/ES/Kubernetes/etc. without an explicit documented requirement.
- **No hardcoded constants** (paths, ports, formula weights) in Python — they belong in `config/pipeline_config.yaml` / `config/spark_config.yaml`. Note: `spark/processing/process_regional_trends.py` currently violates this (hardcoded `hdfs://localhost:9000`) — fix toward config rather than copying the pattern.
- **No fabricated metrics.** Uncomputed → `NOT YET CALCULATED`; unresolved → `DECISION REQUIRED`; guesses → `ASSUMPTION`. Update `docs/Memory.md` after milestones.
- Scope must map directly to the PRD — no invented features.

## Storage mode

`config/pipeline_config.yaml` → `storage.type: hdfs | local` (currently **`local`** → `data/raw`, `data/processed`). HDFS layout is fixed: `/ecommerce/raw/{events,products,inventory}/` (immutable) and `/ecommerce/processed/<module>/`. Develop against `local`; code reading HDFS directly must be gated or documented.

`.gitignore` excludes `data/raw/*`, `data/processed/*`, `*.parquet`, `*.csv.gz`; only `data/sample/*.csv|*.parquet` fixtures are committed (keep `.gitkeep` files).

## Spark rules that differ from pandas defaults (docs/Rules.md §4)

- Never load multi-million-row datasets into pandas; multi-row transforms run in PySpark.
- No `.collect()`/`.toPandas()` on large DataFrames — only small aggregated summaries.
- Broadcast-join the ~5k-row `products` dimension with `functions.broadcast()`.
- Partition raw events by `date=YYYY-MM-DD`; filter on partition keys.
- Persist only DataFrames reused across downstream branches; `unpersist()` after.
- The future dashboard reads **pre-aggregated Parquet only** via `@st.cache_data` — it must never launch Spark jobs on page load.
- Existing sessions: `spark/utils/spark_session.py` (`build_spark_session()`, `local[*]`, shuffle partitions 4) and an inline builder in `process_regional_trends.py`. Prefer the factory; schemas live in `spark/utils/schemas.py`.

## Planned layout & ownership (docs/Architecture.md §9)

Existing: `config/`, `scripts/` (+`data_generation/`, `run_pipeline.py`), `hdfs/`, `spark/` (`utils/`, `preprocessing/`, `processing/`), `requirements.txt`. Missing but planned: `dashboard/`, `tests/`, `notebooks/`.

Ownership: member 1 → `scripts/`+`hdfs/`; member 2 → `spark/` except `pricing/`; member 3 → `spark/pricing/` + `dashboard/`.

## Testing expectations (for when tests are added)

Unit-test the math (demand weights 0.15/0.20/0.30/0.35, arc elasticity, SDR thresholds — exact formulas in `docs/Memory.md` §5) with known expected values; guard division by zero and clamp `|E_d| > 10`. Data generators must stay deterministic (`seed=42` in `generate_events.py`). Tests must run offline with no external services. Dashboard tabs get smoke tests on sample data.

## Other gotchas

- Recommendations must be computed from metrics/thresholds — never hardcoded strings.
- `docs/` links use `file:///c:/Users/...` URLs; don't "fix" them into repo-relative links unless asked.
- `.opencode/opencode.json` loads a local plugin (`.opencode/plugins/graphify.js`); no repo `instructions` are configured there.
- `.opencode/` is untracked — don't commit it unless asked.
