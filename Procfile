web: gunicorn src.app:app
celery: celery -A src.app.celery worker --loglevel=info 
