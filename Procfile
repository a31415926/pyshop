web: gunicorn shop.wsgi --log-file -
release: python manage.py migrate
worker: celery -A shop worker -l info