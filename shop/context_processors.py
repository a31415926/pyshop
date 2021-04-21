from product.models import *

def all_currency(request):
    curr = Currency.objects.all()
    select_curr = request.session.get('curr_id', 'UAH')
    select_curr_info = Currency.objects.get(code = select_curr)
    rate_select_curr = select_curr_info.rate
    disp_select_curr = select_curr_info.disp
    request.session['rate_curr'] = rate_select_curr
    return {
        'all_currency':curr,
        'select_currency':select_curr,
        'rate_select_currency':rate_select_curr,
        'disp_select_currency':disp_select_curr,
    }