from product.models import *

def all_currency(request):
    curr = Currency.objects.all()
    select_curr = request.session.get('curr_id', 'UAH')
    #select_curr_info = Currency.objects.get(code = select_curr)
    rate_select_curr = 0
    disp_select_curr = 'UAH'
    return {
        'all_currency':curr,
        'select_currency':select_curr,
        'rate_select_currency':rate_select_curr,
        'disp_select_currency':disp_select_curr,
    }