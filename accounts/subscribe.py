from accounts import models
import requests

TG_TOKEN = '1729761851:AAHRK8aaNbAMuOj0qis-xOeB9p_rHZu1TPg'

def subscribe_answer_support(id_user, text_answer):
    try:
        user = models.Subscribe.objects.get(user_id = id_user, is_answer_support = True)
    except models.Subscribe.DoesNotExist:
        return False
    
    message = f'Вы получили ответ на ваше обращение: \n\n{text_answer}'
    id_tg = user.user.id_tg
    link = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={id_tg}&parse_mode=Markdown&text={message[:200]}'
    req = requests.get(link)
    