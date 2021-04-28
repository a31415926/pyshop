web: gunicorn shop.wsgi --log-file -
release: python manage.py migrate
worker: celery worker --shop=tasks.app