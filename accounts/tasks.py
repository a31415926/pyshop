from shop.celery import app
from accounts import subscribe
from time import sleep


@app.task
def send_authorizations(id_user, session_key, ip):
    subscribe.subscribe_authorization(id_user, session_key, ip)


@app.task
def send_promo(msg_text):
    sleep(5)
    subscribe.subscribe_promo(msg_text)
