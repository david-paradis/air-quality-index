web: gunicorn src.app
celery: celery -A src.app.celery worker --loglevel=info
