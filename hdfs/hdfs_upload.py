# hdfs/hdfs_upload.py
"""Phase 5: Stage raw datasets to the configured storage backend.

local mode -> verify the local raw/processed staging directories exist.
hdfs mode -> create the HDFS directory tree, upload raw CSVs, and verify
             they exist with `hdfs dfs -ls` (fails loudly if HDFS is absent).
"""
import os
import shutil
import subprocess
import sys

import yaml

RAW_ENTITIES = ["products", "inventory", "events"]


def load_pipeline_config(config_path: str = "config/pipeline_config.yaml") -> dict:
    """Loads localized pipeline parameters safely from config targets."""
    if not os.path.exists(config_path):
        # Fallback dictionary schema if file boundary resolution is blocked
        return {"storage": {"type": "local", "local": {"raw_base": "data/raw",
                                                       "processed_base": "data/processed"}}}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _hdfs(args: list) -> subprocess.CompletedProcess:
    """Run an `hdfs dfs <args>` command and return the completed process."""
    cmd = ["hdfs", "dfs"] + args
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)


def _fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


def run_storage_ingestion() -> None:
    config = load_pipeline_config()
    storage_mode = config["storage"].get("type", "local").lower()

    print(f"🚀 Initializing Phase 5: Storage Routing Engine [Mode: {storage_mode.upper()}]")

    if storage_mode == "local":
        local_raw = config["storage"]["local"]["raw_base"]
        local_processed = config["storage"]["local"]["processed_base"]

        os.makedirs(local_processed, exist_ok=True)
        missing = [e for e in RAW_ENTITIES
                   if not os.path.exists(os.path.join(local_raw, e, f"{e}.csv"))]
        if missing:
            _fail(f"Raw datasets missing for staging: {missing}. Run generate_all.py first.")
        print(f"✅ Local File System verified. Directories mapped to '{local_raw}' and '{local_processed}'.")
        print("Data blocks are fully staged and prepared for Phase 6 Spark transformation runs.")
        return

    if storage_mode == "hdfs":
        hdfs_raw = config["storage"]["hdfs"]["raw_base"]
        hdfs_processed = config["storage"]["hdfs"]["processed_base"]

        if shutil.which("hdfs") is None:
            _fail("'hdfs' CLI not found on PATH. Install Hadoop, set HADOOP_HOME, start the "
                  "daemons (start-dfs.cmd), or switch storage.type to 'local'. "
                  "HDFS upload NOT VERIFIED.")

        # 1. Directory creation: /ecommerce/raw/<entity>/ + /ecommerce/processed/
        for entity in RAW_ENTITIES:
            result = _hdfs(["-mkdir", "-p", f"{hdfs_raw}/{entity}"])
            if result.returncode != 0:
                _fail(f"Could not create {hdfs_raw}/{entity}: {result.stderr.strip()}")
        result = _hdfs(["-mkdir", "-p", hdfs_processed])
        if result.returncode != 0:
            _fail(f"Could not create {hdfs_processed}: {result.stderr.strip()}")
        print(f"✅ HDFS directory tree ready under {hdfs_raw}/ and {hdfs_processed}/")

        # 2. Upload (raw zone is write-once; -put -f allows safe re-runs)
        for entity in RAW_ENTITIES:
            local_source = f"data/raw/{entity}/{entity}.csv"
            hdfs_target = f"{hdfs_raw}/{entity}"
            if not os.path.exists(local_source):
                _fail(f"Missing local source file: {local_source}. Run generate_all.py first.")
            print(f"-> Uploading {local_source} to {hdfs_target}/")
            result = _hdfs(["-put", "-f", local_source, f"{hdfs_target}/"])
            if result.returncode != 0:
                _fail(f"hdfs dfs -put failed for {entity}: {result.stderr.strip()}")

        # 3. Verification: list every uploaded file (do not claim success without evidence)
        print("🔍 Verifying uploads with `hdfs dfs -ls` ...")
        for entity in RAW_ENTITIES:
            remote = f"{hdfs_raw}/{entity}/{entity}.csv"
            result = _hdfs(["-ls", remote])
            if result.returncode != 0:
                _fail(f"Verification failed, file not found in HDFS: {remote}")
            print(f"   ✅ {remote}")
            print(f"      {result.stdout.strip().splitlines()[-1]}")

        print("✅ HDFS ingestion complete and verified: raw datasets present in the cluster.")


if __name__ == "__main__":
    run_storage_ingestion()
