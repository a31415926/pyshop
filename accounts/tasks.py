from shop.celery import app
from accounts import subscribe


@app.task
def send_authorizations(id_user, session_key, ip):
    subscribe.subscribe_authorization(id_user, session_key, ip)


@app.task
def send_promo(msg_text):
    subscribe.subscribe_promo(msg_text)


@app.task
def send_create_order(id_user, id_order, url_order):
    subscribe.subscribe_create_order(id_user, id_order, url_order)