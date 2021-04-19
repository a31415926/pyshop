from django import forms
from product.models import Order, OrderItem, Promocode


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'full_amount', 'total_amount', 'currency', 'rate_currency',
        'promo', 'delivery_method', 'cost_of_delivery']


class ChangeStatusOrder(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status',]

class CreatePromo(forms.ModelForm):
    class Meta:
        model = Promocode
        fields = ['code', 'type_code', 'amount_of_discount', 'type_promo', 'status', 'start_promo', 'end_promo']