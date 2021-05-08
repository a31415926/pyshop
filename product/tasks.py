from shop.celery import app
from time import sleep


@app.task
def test_celery(cnt):
    for i in range(cnt):
        sleep(0.5)
        print(i)