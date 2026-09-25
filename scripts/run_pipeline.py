# scripts/run_pipeline.py
import os
import sys
import subprocess

def run_step(command_list, step_name):
    """Executes a system process step and tracks execution codes."""
    print(f"\n==================================================")
    print(f"🎬 STARTING STEP: {step_name}")
    print(f"==================================================")
    
    try:
        # Run subprocess and stream output directly to terminal console nodes
        process = subprocess.run(command_list, check=True)
        print(f"🚀 SUCCESS: Finished {step_name} cleanly.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CRITICAL BREAKDOWN: {step_name} failed with exit code {e.returncode}")
        return False

def main():
    print("==================================================")
    print("🚀 GEOSPATIAL E-COMMERCE BIG DATA PIPELINE ENGINE 🚀")
    print("==================================================")
    
    # Define project path boundaries based on local execution context
    python_exe = sys.executable
    
    # Sequence Step 1: Synthetic Dataset Generation Suite (Phase 3)
    gen_cmd = [python_exe, "scripts/data_generation/generate_all.py", "--scale", "dev"]
    if not run_step(gen_cmd, "Phase 3 - Synthetic Dataset Generation"):
        sys.exit(1)
        
    # Sequence Step 2: PySpark Schema and Bounds Validation (Phase 4)
    val_cmd = [python_exe, "spark/preprocessing/validate_records.py"]
    if not run_step(val_cmd, "Phase 4 - PySpark Integrity Validation"):
        sys.exit(1)
        
    # Sequence Step 3: Local Storage / HDFS Data Lake Staging Ingestion (Phase 5)
    upload_cmd = [python_exe, "hdfs/hdfs_upload.py"]
    if not run_step(upload_cmd, "Phase 5 - Storage Ingestion & Path Routing"):
        sys.exit(1)
        
    print("\n==================================================")
    print("🎉 ALL INGESTION PIPELINE STAGES COMPLETED CLEANLY 🎉")
    print("Your data lake staging environment is fully verified.")
    print("Ready to hand off to Team Member 2 for Analytics processing jobs.")
    print("==================================================")

if __name__ == "__main__":
    main()
