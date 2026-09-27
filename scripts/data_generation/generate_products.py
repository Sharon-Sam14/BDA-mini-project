import pandas as pd
import random

CATEGORIES = ["Electronics", "Apparel", "Home Appliances", "Sports Equipment", "Footwear", "Beauty", "Books", "Groceries"]

def generate_product_catalog(num_products=5000):
    products = []
    for i in range(1, num_products + 1):
        products.append({
            "product_id": f"PRD_{i:05d}",
            "product_name": f"Product Item {i}",
            "category": random.choice(CATEGORIES),
            "base_price": round(random.uniform(299.0, 89999.0), 2)
        })
    df = pd.DataFrame(products)
    df.to_csv("data/raw/products/products.csv", index=False)
    return df
