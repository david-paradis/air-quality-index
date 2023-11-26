from flask import Flask, request, render_template
import requests
import os
from celery import Celery
from dotenv import load_dotenv
from tasks.fetch_historical_data import fetch_and_store_historical_data

load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'default_broker_url')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'default_backend_url')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

WAQI_API_KEY = os.getenv('WAQI_API_KEY', 'default_api_key')

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
    response = requests.get(f'http://api.waqi.info/feed/{city}/?token={WAQI_API_KEY}')
    return response.json()


@celery.task
def fetch_historical_data(city):
    fetch_and_store_historical_data(city, WAQI_API_KEY)

if __name__ == '__main__':
    app.run(debug=True)