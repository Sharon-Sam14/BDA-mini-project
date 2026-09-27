import pandas as pd
import random
import uuid
from faker import Faker
from geo_metadata import get_cities_df

fake = Faker('en_IN')

def generate_clickstream(products_df, num_records=100000, seed=42):
    random.seed(seed)
    Faker.seed(seed)
    
    cities_df = get_cities_df()
    events = []
    prod_list = products_df.to_dict('records')
    city_list = cities_df.to_dict('records')
    
    event_types = ["search", "view", "cart", "purchase"]
    event_weights = [0.40, 0.35, 0.15, 0.10]
    
    for _ in range(num_records):
        product = random.choice(prod_list)
        location = random.choice(city_list)
        event = random.choices(event_types, weights=event_weights)[0]
        
        qty = random.randint(1, 4) if event == "purchase" else 1
        discount = round(random.uniform(0.05, 0.65), 2) if random.random() > 0.7 else 0.0
        final_price = round(product["base_price"] * (1 - discount), 2)
        
        events.append({
            "event_id": str(uuid.uuid4()),
            "user_id": f"USR_{random.randint(10000, 99999)}",
            "product_id": product["product_id"],
            "timestamp": fake.date_time_between(start_date='-30d', end_date='now').strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event,
            "city": location["city"],
            "state": location["state"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "price": final_price,
            "discount_percent": int(discount * 100),
            "quantity": qty
        })
        
    df = pd.DataFrame(events)
    df.to_csv("data/raw/events/events.csv", index=False)
    return df
