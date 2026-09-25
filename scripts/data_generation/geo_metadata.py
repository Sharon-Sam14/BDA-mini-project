import pandas as pd

INDIAN_CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
    {"city": "Pune", "state": "Maharashtra", "latitude": 18.5204, "longitude": 73.8567},
    {"city": "Bengaluru", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946},
    {"city": "Delhi", "state": "Delhi", "latitude": 28.7041, "longitude": 77.1025},
    {"city": "Nashik", "state": "Maharashtra", "latitude": 19.9975, "longitude": 73.7898},
    {"city": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882},
    {"city": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867},
    {"city": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707}
]

def get_cities_df():
    return pd.DataFrame(INDIAN_CITIES)
