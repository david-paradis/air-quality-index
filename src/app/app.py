from flask import Flask, request, render_template
import requests
import os
from celery import Celery
from dotenv import load_dotenv
from pymongo import MongoClient

from .tasks.fetch_historical_data import fetch_and_store_historical_data

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'default_broker_url')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'default_backend_url')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

WAQI_API_KEY = os.getenv('WAQI_API_KEY', 'demo')

# Configure MongoDB client
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/mydatabase')
client = MongoClient(mongo_uri)
db = client.get_default_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        aqi_data = get_aqi(city) # Real time data
        fetch_historical_data.delay(city)  # Start async task to gather historical data for this city
        return render_template('results.html', aqi_data=aqi_data)
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    city = request.form['city']
    aqi_data = get_aqi(city)
    return render_template('results.html', aqi_data=aqi_data)

def get_aqi(city):
    # Use the WAQI API to get the current AQI data
    response = requests.get(f'https://api.waqi.info/search/?keyword={city}&token={WAQI_API_KEY}')
    # TODO Handle error (ex quota exceeded, nothing found, etc)
    return response.json()['data'][0]


@celery.task
def fetch_historical_data(city):
    fetch_and_store_historical_data(city, WAQI_API_KEY)

if __name__ == '__main__':
    app.run(debug=True)