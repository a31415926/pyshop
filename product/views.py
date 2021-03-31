from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect, HttpResponse
from product.models import *
from django.urls import reverse
from django.forms.models import model_to_dict
from product import forms
from accounts import models
from product import services
import json
import requests


def shop_main_page(request):
    categories = Categories.objects.all()
    return render(request, 'product/main_page.html', context={'category':categories})

def category_page(request, pk):
    category = Product.objects.filter(cid=pk)
    return render(request, 'product/category_page.html', context={'products':category})

def product_page(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'product/product_page.html', context={'product':product})

def select_curr(request):
    if request.method == 'POST':
        link = request.META.get('HTTP_REFERER')
        request.session['curr_id'] = request.POST.get('all_currency')
        return HttpResponseRedirect(link)

def basket(request):
    if request.method == 'POST':
        link = request.META.get('HTTP_REFERER')
        type_basket = request.POST.get('type')
        product_id = request.POST.get('id')
        #защита от дурака, чтобы не отправили null, дефолтное будет 1
        product_cnt = request.POST.get('cnt', 1)
        product_cnt = 1 if not product_cnt else product_cnt
        product_info = model_to_dict(get_object_or_404(Product, id = product_id))
        del(product_info['cid'])
        del(product_info['photo'])
        
        if not request.session.get('basket'):
            request.session['basket'] = {}
        if type_basket == 'add':
            if not request.session['basket'].get(str(product_id)):
                request.session['basket'][str(product_id)] = product_info
            now_qty = request.session['basket'][str(product_id)].get('qty', 0)
            request.session['basket'][str(product_id)]['qty'] = now_qty + int(product_cnt)
            data_response = {'success': f'Добавлено в корзину {product_cnt} товаров'}
        elif type_basket == 'del':
            del(request.session['basket'][str(product_id)])
            html_result = ""
            for prodoct_id, product_val in request.session['basket'].items():
                html_result += f'<tr><th scope="row">1</th>'
                html_result += f'<td><a href=\'{reverse("product_page", kwargs={"pk":product_id})}\'">{product_val["title"]}</a></td>'
                html_result += f'<td>посчитать</td>'
                html_result += f'<td>{product_val["qty"]}</td>'
                html_result += f'<td><button type=\'submit\' onclick="del_basket({product_id})">X</button></td>'
                html_result += '</tr>'
                    
            html_result += ''
            data_response = {'success':'Удалено', 'responce':html_result}

        return HttpResponse(json.dumps(data_response), content_type = 'application/json')


def checkout_page(request):
    if not request.session.get('basket'):
        request.session['basket'] = {}
    basket = request.session['basket']
    total_cost = 0
    for i in basket.values():
        total_cost += i['qty'] * i['price']
    delivery = Delivery.objects.all()
    if request.method == 'POST':
        data = request.POST.copy()
        order_currency = Currency.objects.get(code = request.session.get('curr_id', 'UAH'))
        promocode = data.get('promo_code')
        is_promo = False
        if promocode:
            is_promo = Promocode.is_promo(data.get('promo_code'))
            if is_promo:
                data['promo'] = Promocode.objects.get(code = data['promo_code'])
        discount = Promocode.get_discount(total_cost, data['promo_code']) if is_promo else 0
        data['user'] = request.user if request.user.is_authenticated else ''
        data['full_amount'] = total_cost
        data['total_amount'] = total_cost + discount
        data['full_amount_on_curr'] = total_cost*order_currency.rate
        data['total_amount_on_curr'] = data['total_amount'] * order_currency.rate
        data['currency'] = order_currency
        data['rate_currency'] = order_currency.rate
        create_order = forms.OrderForm(data)
        print(create_order.errors)

        if create_order.is_valid() and basket:
            new_order = create_order.save()
            for good in basket.values():
                OrderItem.objects.create(
                    id_good = good['id'], 
                    title_good = good['title'],
                    cost = good['price'],
                    cost_on_curr = good['price'] * order_currency.rate,
                    order = new_order,
                    qty = good['qty'],
                )

            return redirect('invoice_page', new_order.id)  

    return render(request, 'product/checkout_page.html', context={'products':basket, 'total_cost':total_cost, 'all_delivery':delivery})


def all_invoices(request):
    """ страница со всеми заказами """
    template = 'product/all_invoices.html'
    context = {}
    all_invoices = Order.objects.all()
    all_status = forms.ChangeStatusOrder()
    context['all_invoices'] = all_invoices
    context['all_status'] = all_status
    return render(request, template, context=context)


def change_invoice(request):
    """ смена статуса заказа """
    if request.method == 'POST':
        link = request.META.get('HTTP_REFERER')
        Order.change_status(request.POST.get('id_order'), request.POST.get('status'))

        return HttpResponseRedirect(link)    


def get_invoice(request, pk):
    template = 'product/invoice_page.html'
    context = {}
    order = get_object_or_404(Order, pk=pk)
    goods = order.orderitem_set.all()
    if request.user.is_authenticated and order.user:
        if request.user.id == order.user.id:
            user_balance = order.user.balance
            if user_balance >= order.total_amount_on_curr and order.status != 'paid':
                context['pay'] = True

    if order.status == 'paid' and request.user.has_perm('product.change_status'):
        context['cancel_order'] = True

    if request.method == 'POST':
        data = request.POST
        meta = data.get('mode')
        if meta == 'pay_order':
            if context.get('pay'):
                Order.change_status(pk, 'paid')
                order.user.balance -= order.total_amount_on_curr
                order.user.save()
                context['pay'] = False
        elif meta=='cancel_order' and context.get('cancel_order'):
                Order.change_status(pk, 'cancel')
                order.user.balance += order.total_amount_on_curr
                order.user.save()
                context['pay'] = True
                context['cancel_order'] = False

    context['order'] = order
    context['goods'] = goods
    return render(request, template, context=context)


def edit_invoice(request, pk):
    template = 'product/invoice_edit_page.html'
    context = {}
    order = get_object_or_404(Order, pk=pk)
    goods = order.orderitem_set.all()
    context['order'] = order
    if request.method == 'POST':
        mode  = request.POST.get('mode') 
        print(request.POST)
        data = request.POST
        if mode == 'edit_invoice':
            full_amount = 0
            for good in goods:
                edit_price = data.get(f'price_{good.id}')
                edit_qty = data.get(f'qty_{good.id}')
                del_good = data.get(f'del_{good.id}')
                if edit_price and edit_qty:
                    if del_good:
                        OrderItem.objects.get(pk = good.id).delete()
                        continue
                    edit_price = float(edit_price)
                    full_amount += edit_price * int(edit_qty) / order.rate_currency
                    order_item = OrderItem.objects.get(pk = good.id)
                    order_item.qty = int(edit_qty)
                    order_item.cost_on_curr = edit_price
                    order_item.save()
                    order.full_amount = full_amount
                    order.full_amount_on_curr = full_amount * order.rate_currency
                    discount = 0
                    if order.promo:
                        discount = Promocode.get_discount(full_amount, order.promo.code)
                    order.total_amount = full_amount + discount
                    order.total_amount_on_curr = (full_amount + discount) * order.rate_currency
                    order.save()
            goods = order.orderitem_set.all()
        
        elif mode == 'add_good':
            id_good = data['id_good']
            product = get_object_or_404(Product, pk = id_good)
            obj, create_item = OrderItem.objects.get_or_create(
                    order=order, 
                    id_good = id_good, 
                    defaults= {
                        'cost_on_curr':product.price * order.rate_currency,
                        'title_good':product.title
                        }
            )
            print(obj, create_item)

            if not create_item:
                obj.qty += 1
                obj.save()
            order.total_amount_on_curr += product.price * order.rate_currency
            order.save()
    context['goods'] = goods
                
            
    return render(request, template, context=context)


def create_promocode(request):
    template = 'product/create_promocode_page.html'
    form = forms.CreatePromo()
    if request.method == 'POST':
        create_code = forms.CreatePromo(request.POST)
        if create_code.is_valid():
            create_code.save()
    return render(request, template, context={'form':form})


def edit_price_in_category(request):
    template = 'product/edit_price_in_category.html'
    context = {}
    categories = Categories.objects.all()
    context['categories'] = categories
    if request.method == 'POST':
        data = request.POST
        data_for_edit = services.ProductServices.data_preparation_edit_price(data)
        products = services.ProductServices.get_all_products_in_categories(data_for_edit['lst_cats_id'])
        services.ProductServices.edit_price_products(
            products = products, 
            type_edit = data_for_edit['type_edit'], 
            value_edit = data_for_edit['value_edit'], 
            is_edit_old_price = data_for_edit['is_edit_old_price']
        )

    return render(request, template, context)


def export_products(request):
    template = 'product/export.html'
    context = {}
    if request.method == 'POST':
        type_file = request.POST.get('type', 'csv')
        services.ProductServices.export_to_file(type_file)
    return render(request, template, context)

def import_products(request):
    template = 'product/import.html'
    context = {}
    if request.method == 'POST':
        data = request.POST
        type_import = data.get('type')
        link_price = data.get('link')
        data_response = {}
        is_valid_link = services.ImportSheet.is_correct_link(link_price)
        if type_import == 'import':
            if is_valid_link:
                data_response['success'] = '<b>Выполняется обработка прайса..</b>'
                services.ImportSheet.import_from_gsheets(link_price)
            else:
                data_response['error'] = 'Файл по указанной сыслке недоступен.'
        elif type_import == 'preview':
            if is_valid_link:
                lst_on_preview = services.ImportSheet.import_from_gsheets(link_price, preview=True)
                data_response['success'] = services.ImportSheet.generate_preview_to_front(lst_on_preview)
                data_response['preview'] = True

        return HttpResponse(json.dumps(data_response), content_type = 'application/json')

    return render(request, template)