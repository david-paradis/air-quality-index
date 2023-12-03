import pandas as pd
from src.app.helpers import normalize_city_name
from bson import ObjectId
from pymongo import MongoClient
import os

def fetch_and_store_historical_data(city):
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/air-quality-index'), 
                         username=os.getenv('MONGO_USERNAME', ''),
                         password=os.getenv('MONGO_PASSWORD', ''))
    db = client.get_default_database()
    
    # Configuration variables
    csv_file_path = os.getenv('DATA_FILE_PATH','data/waqi-covid-2023.csv')
    collection = db['aqi-measurements']

    # Read the CSV file using pandas
    data = pd.read_csv(csv_file_path, on_bad_lines='skip')

    # Apply normalization to the 'City' column in the DataFrame
    data['City'] = data['City'].apply(normalize_city_name)


    normalized_city = normalize_city_name(city)

    # Only select the rows for the selected city
    data = data.loc[(data['City'] == normalized_city) & (data['Specie'] == 'pm25')]

    # Iterate over the DataFrame rows and insert into MongoDB
    for index, row in data.iterrows():
        document = transform_row(row)
        unique_identifier = {"city": normalized_city, "date": document["date"]}

        collection.update_one(unique_identifier, {"$set": document}, upsert=True)

    client.close()

    return normalized_city

# Helper function to transform a row 
def transform_row(row):
    return {
        "date": row['Date'], 
        "country": row['Country'],
        "city": row['City'],
        "aqi": row['median']
    }