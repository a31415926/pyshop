from accounts.models import *
from product.models import *
import requests
import json


TG_TOKEN = '1729761851:AAHRK8aaNbAMuOj0qis-xOeB9p_rHZu1TPg'


def geo_ip_info(ip_address):
    req = requests.get(f'http://ipwhois.app/json/{ip_address}').json()
    response = {}
    if req.get('success'):
        response['county'] = req.get('county')
        response['region'] = req.get('region')
        response['city'] = req.get('city')
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


def subscribe_authorization(id_user, session_key, ip):
    try:
        user = Subscribe.objects.get(user_id = id_user, is_authorization = True)
    except Subscribe.DoesNotExist:
        return False
    
    ip_info = geo_ip_info(ip)
    str_ip_info = '/'.join(ip_info.values())
    message = f'В ваш аккаунт был выполнен вход с IP-адреса {ip} ({str_ip_info})\nЕсли это были не вы - нажмите кнопку ниже.'
    id_tg = user.user.id_tg
    link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message}'
    req = requests.get(link)


def subscribe_promo(text_msg):
    users = Subscribe.objects.filter(is_promo = True)
    message = text_msg
    for user in users:
        id_tg = user.user.id_tg
        link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=HTML&text={message[:200]}'
        req = requests.get(link)
    
    
def subscribe_get_file_in_order(id_user, id_order):
    try:
        order = Order.objects.get(pk = id_order)
        user = Subscribe.objects.get(user_id = id_user, is_get_digit_file = True)
    except (Order.DoesNotExist, Subscribe.DoesNotExist):
        return False
    all_files = order.orderitem_set.all()
    for item in all_files:
        try:
            product = Product.objects.get(pk=item.id_good)
        except Product.DoesNotExist:
            return False
    
        if product.type_product == 'file':
            files = {'document':(product.file_digit.name, product.file_digit)}
            link = f'https://api.telegram.org/bot{TG_TOKEN}/sendDocument?chat_id=456008920&parse_mode=HTML'
            req = requests.post(link, files = files)
