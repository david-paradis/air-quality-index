import os
import pandas as pd

from src.app.helpers import normalize_city_name

def analyze_historical_data(city):
    from pymongo import MongoClient

    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/air-quality-index'), 
                         username=os.getenv('MONGO_USERNAME', ''),
                         password=os.getenv('MONGO_PASSWORD', ''))
    db = client.get_default_database()
    
    # Fetch historical data from database
    normalized_city = normalize_city_name(city)
    historical_data = list(db['aqi-measurements'].find({'city': normalized_city}))

    if not historical_data:
        return {"error": "No historical data found for the city"}

    df = pd.DataFrame(historical_data)

    min_aqi = df['aqi'].min()
    max_aqi = df['aqi'].max()
    min_date = df[df['aqi'] == min_aqi]['date'].iloc[0]
    max_date = df[df['aqi'] == max_aqi]['date'].iloc[0]
    average_aqi = round(df['aqi'].mean(), 2)

    # Prepare and return results
    analysis_results = {
        "city": normalized_city,
        "avg_aqi": average_aqi,
        "min_aqi": min_aqi,
        "max_aqi": max_aqi,
        "min_date": str(min_date),
        "max_date": str(max_date)
    }

    client.close()

    return analysis_results
