# scripts/data_generation/generate_all.py
import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_products import generate_product_catalog
from generate_inventory import generate_warehouse_stock
from generate_events import generate_clickstream

def main():
    parser = argparse.ArgumentParser(description="Geo-Spatial Generation Framework")
    parser.add_argument("--scale", type=str, default="dev", choices=["dev", "demo", "benchmark"])
    args = parser.parse_args()
    
    scale_map = {"dev": 100000, "demo": 1000000, "benchmark": 10000000}
    records = scale_map[args.scale]
    
    # Ensure physical folder directories exist securely on Windows filesystem nodes
    for entity in ['products', 'inventory', 'events']:
        os.makedirs(f"data/raw/{entity}", exist_ok=True)
        
    print(f"⚙️ Building database files for profile size: {records} rows.")
    p_df = generate_product_catalog(num_products=1000 if args.scale == "dev" else 5000)
    generate_warehouse_stock(p_df)
    generate_clickstream(p_df, num_records=records)
    print("🎉 Phase 3 completed. Target CSV files successfully staged in data/raw/")

if __name__ == "__main__":
    main()
