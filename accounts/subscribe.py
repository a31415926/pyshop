from shop.settings import SITE_URL
from accounts.models import *
from product import models as models_shop
import requests
import json
from dotenv import load_dotenv
load_dotenv()
import os


TG_TOKEN = os.environ.get('TG_TOKEN')


def geo_ip_info(ip_address):
    req = requests.get(f'http://ipwhois.app/json/{ip_address}').json()
    response = {}
    if req.get('success'):
        response['country'] = req.get('country') if req.get('country') else ''
        response['region'] = req.get('region') if req.get('region') else ''
        response['city'] = req.get('city') if req.get('city') else ''
    return response


def subscribe_answer_support(id_user, text_answer):
    try:
        user = Subscribe.objects.get(user_id = id_user, is_answer_support = True)
    except Subscribe.DoesNotExist:
        return False
    
    message = f'Вы получили ответ на ваше обращение: \n\n{text_answer}'
    id_tg = user.user.id_tg
    link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message[:200]}'
    req = requests.get(link)


def subscribe_create_order(id_user, id_order, url_order):
    try:
        user = Subscribe.objects.get(user_id = id_user, is_create_order = True)
    except Subscribe.DoesNotExist:
        return False
    
    message = f'Вы оформили заказ с ID {id_order}\nСсылка на заказ: {SITE_URL}{url_order}'
    id_tg = user.user.id_tg
    link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message}'
    req = requests.get(link)
    print(link)
    print(req.text)


def subscribe_authorization(id_user, session_key, ip):
    try:
        user = Subscribe.objects.get(user_id = id_user, is_authorization = True)
    except Subscribe.DoesNotExist:
        return False
    
    ip_info = geo_ip_info(ip)
    str_ip_info = '/'.join(ip_info.values())
    message = f'В ваш аккаунт был выполнен вход с IP-адреса {ip} ({str_ip_info})\nЕсли это были не вы - нажмите кнопку ниже.'
    id_tg = user.user.id_tg
    link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message}&reply_markup={{"inline_keyboard":[[{{"text":"Закрыть сеанс","callback_data":"link"}}]]}}'
    req = requests.get(link)


def subscribe_promo(text_msg):
    users = Subscribe.objects.filter(is_promo = True)
    message = text_msg
    for user in users:
        id_tg = user.user.id_tg
        link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message[:200]}'
        req = requests.get(link)
        print(req.json())
    
    
def subscribe_get_file_in_order(id_order):
    try:
        order = models_shop.Order.objects.get(pk = id_order)
        user = Subscribe.objects.get(user_id = order.user, is_get_digit_file = True)
    except (models_shop.Order.DoesNotExist, Subscribe.DoesNotExist):
        return False
    all_files = order.orderitem_set.all()
    for item in all_files:
        try:
            product = models_shop.Product.objects.get(pk=item.product.id)
        except models_shop.Product.DoesNotExist:
            return False
    
        if product.type_product == 'file':
            token_file = product.filetelegram_set.all()
            file_id = ''
            link = f'https://api.telegram.org/bot{TG_TOKEN}/sendDocument?chat_id={user.user.id_tg}&parse_mode=HTML'
            if token_file:
                file_id = token_file.first().id_file
                files = {'document':file_id}
                req = requests.post(link, data=files)
            else:
                files = {'document':(product.file_digit.name, product.file_digit)}
                req = requests.post(link, files = files)
                if req.status_code == 200:
                    new_token = req.json()
                    new_token = new_token['result']['document']['file_id']
                    models_shop.FileTelegram.objects.update_or_create(
                        product = product,
                        defaults = {'id_file':new_token}
                    )


def subscribe_edit_price(lst, name, new_price):
    message = f'Изменилась цена на товар {name}\nНовая цена - {new_price}'
    for id_tg in lst:
        link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message[:200]}'
        req = requests.get(link)


def subscribe_active_product(lst, product_name, price, items):
    message = f'Товар "{product_name}" снова в наличии! Успей купить по цене {price}'
    for id_tg in lst:
        link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message[:200]}'
        req = requests.get(link)
        print(req.json())
    all_items = models_shop.SubActivateProduct.objects.filter(pk__in = items)
    all_items.delete()