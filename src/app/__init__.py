from urllib.parse import unquote
from .helpers import normalize_city_name
from flask import Flask, request, render_template, jsonify
import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from celery.signals import task_success
from celery import Celery

from .tasks.fetch_historical_data import fetch_and_store_historical_data
from .tasks.analyze_historical_data import analyze_historical_data
from .models.air_quality_measurement import AirQualityMeasurement

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL', 'amqp://guest:guest@rabbitmq:5672//'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'rpc://')
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/air-quality-index'), 
                         username=os.getenv('MONGO_USERNAME', ''),
                         password=os.getenv('MONGO_PASSWORD', ''))
db = client.get_default_database()


# Declare tasks
@celery.task(name='fetch_and_store_historical_data')
def async_fetch_historical(city):
    return fetch_and_store_historical_data(city)

@celery.task(name='analyze_historical_data')
def async_analyze_historical(city):
    return analyze_historical_data(city)

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    if sender.name == 'fetch_and_store_historical_data':
        # Trigger the analysis task
        async_analyze_historical.delay(result)
    if sender.name == 'analyze_historical_data':
        # Store the analysis result
        store_analysis_result(result)
        
WAQI_API_KEY = os.getenv('WAQI_API_KEY', 'demo')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    city = request.form['city']
    normalized_city = normalize_city_name(city)
    aqi_data = get_aqi(normalized_city)
    aqm = None
    if aqi_data and isinstance(aqi_data, dict) and 'aqi' in aqi_data and 'station' in aqi_data and aqi_data['aqi'] != '-':
        aqm = AirQualityMeasurement(city, aqi_data['aqi'], aqi_data['station']['name'])
        async_fetch_historical.delay(city)
    else:
        aqm = AirQualityMeasurement(city, -1)   
    return render_template('results.html', aqm=aqm)


# Route to check data analysis task status
@app.route('/check_historical/<city>', methods=['GET'])
def check_historical_data(city):
    # Retrieve results from where you stored them
    decoded_city = unquote(city)  # Decode URL-encoded city name
    normalized_city = normalize_city_name(decoded_city)  # Normalize city name
    historical_analysis = db['analysis-tasks'].find_one({"_id": normalized_city})  # Retrieve stored analysis data
    if historical_analysis is None:
        return jsonify({"status": "PENDING"})
    return jsonify({"status": "READY", "data": historical_analysis['result']})

def get_aqi(city):
    # Use the WAQI API to get the current AQI data
    response = requests.get(f'https://api.waqi.info/search/?keyword={city}&token={WAQI_API_KEY}')
    if response.status_code != 200 or len(response.json()['data']) == 0:
        return None
    return response.json()['data'][0]

def store_analysis_result(result):
    # Store the analysis result in the database
    document = {
        "_id": result['city'],
        "result": result
    }
    db['analysis-tasks'].update_one({"_id": result['city'], "result": result}, {"$set": document}, upsert=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
