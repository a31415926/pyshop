from django.urls import include, path
from product.views import *


urlpatterns = [
    path('shop/', shop_main_page, name='main_page'),
    path('shop/currency', select_curr, name='category_page'),
    path('shop/category/<int:pk>/', category_page, name='category_page'),
    path('shop/product/<int:pk>/', product_page, name='product_page'),
    path('shop/basket/', basket, name='basket_page'),
    path('shop/checkout/', checkout_page, name='checkout_page'),
    path('shop/create_promocode/', create_promocode, name='create_promocode_page'),
    path('shop/invoices/', all_invoices, name='invoices_page'),
    path('shop/change_invoice/', change_invoice, name='change_invoice'),
    path('shop/invoice/<int:pk>/', get_invoice, name='invoice_page'),
    path('shop/invoice/<int:pk>/edit/', edit_invoice, name='invoice_edit_page'),
    path('shop/edit_price_in_category/', edit_price_in_category, name='edit_price_in_category'),
    path('shop/export/', export_products, name='export_products'),
    path('shop/import/', import_products, name = 'import_products'),
]