import pandas as pd
import random
from geo_metadata import get_cities_df

def generate_warehouse_stock(products_df):
    cities_df = get_cities_df()
    inventory = []
    
    for _, city_row in cities_df.iterrows():
        for _, prod_row in products_df.iterrows():
            inventory.append({
                "product_id": prod_row["product_id"],
                "city": city_row["city"],
                "available_stock": random.choices([0, random.randint(5, 450)], weights=[0.1, 0.9])[0],
                "date": "2026-09-25"
            })
            
    df = pd.DataFrame(inventory)
    df.to_csv("data/raw/inventory/inventory.csv", index=False)
    return df
    