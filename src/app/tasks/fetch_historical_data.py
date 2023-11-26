import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from dateutil import parser

def fetch_and_store_historical_data(city):
    # Configuration variables
    csv_file_path = 'path_to_your_csv_file.csv'
    mongo_uri = 'mongodb_connection_string'  # e.g., 'mongodb://localhost:27017'
    db_name = 'your_database_name'
    collection_name = 'your_collection_name'

    # Establish a connection to the MongoDB server
    client = MongoClient(mongo_uri)

    # Select the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Read the CSV file using pandas
    data = pd.read_csv(csv_file_path)

    # TODO Only select the rows for the city

    # Iterate over the DataFrame rows and insert into MongoDB
    for index, row in data.iterrows():
        document = transform_row(row)
        collection.insert_one(document)

    # Close the connection to MongoDB
    client.close()

# Helper function to transform a row 
def transform_row(row):
    return {
        "_id": ObjectId(),
        "country": row['Country'],
        "city": row['City'],
        "specie": row['Specie'],
        "readings": [
            {"timestamp": parser.parse(f"{row['Date']}T{hour}:00:00Z"), "value": value}
            for hour, value in row[['01:00', '02:00', ..., '24:00']].items()  # Replace with actual hour columns
        ],
        "summary": {
            "count": row['count'],
            "min": row['min'],
            "max": row['max'],
            "median": row['median'],
            "variance": row['variance']
        }
    }