# backend/app.py
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)

# Apply global configuration allowing browser clients to access endpoints cleanly
CORS(app, support_credentials=True)

# Define the absolute root project directory path safely
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Map the data locations explicitly based on the root project baseline path
REGIONAL_TRENDS_PATH = os.path.join(BASE_DIR, "data", "processed", "regional_trends")
DEMAND_SCORES_PATH = os.path.join(BASE_DIR, "data", "processed", "demand_scores")

@app.route("/api/regional-trends", methods=["GET"])
def get_regional_trends():
    try:
        # Check if PySpark has completed writing the data blocks locally
        if not os.path.exists(REGIONAL_TRENDS_PATH):
            return jsonify({"status": "error", "message": "Regional trends Parquet folder not found. Run Spark first."}), 404
            
        # Read the split snappy parquet folder directly using pandas vector engines
        df = pd.read_parquet(REGIONAL_TRENDS_PATH)
        data_records = df.to_dict(orient="records")
        
        return jsonify({
            "status": "success",
            "total_records": len(data_records),
            "data": data_records
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/demand-scores", methods=["GET"])
def get_demand_scores():
    try:
        # Check if PySpark has completed writing the demand scores locally
        if not os.path.exists(DEMAND_SCORES_PATH):
            return jsonify({"status": "error", "message": "Demand scoring Parquet folder not found. Run Spark first."}), 404
            
        df = pd.read_parquet(DEMAND_SCORES_PATH)
        # Cap the output arrays to the top 25 high-intensity product rows for UI speed efficiency
        data_records = df.head(25).to_dict(orient="records")
        
        return jsonify({
            "status": "success",
            "total_records": len(data_records),
            "data": data_records
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Add this endpoint inside your backend/app.py script layout:
@app.route("/api/supply-demand", methods=["GET"])
def get_supply_demand():
    try:
        MISMATCH_PATH = os.path.join(BASE_DIR, "data", "processed", "supply_demand")
        if not os.path.exists(MISMATCH_PATH):
            return jsonify({"status": "error", "message": "Supply-Demand data path not found. Run Spark script."}), 404
            
        df = pd.read_parquet(MISMATCH_PATH)
        # Pull down records for UI processing views evaluation
        data_records = df.to_dict(orient="records")
        
        return jsonify({
            "status": "success",
            "total_records": len(data_records),
            "data": data_records
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Launch on Port 5000 securely
    app.run(host="127.0.0.1", port=5000, debug=True)
