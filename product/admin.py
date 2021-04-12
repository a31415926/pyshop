from django.contrib import admin
from product.models import *


admin.site.register(Categories)
admin.site.register(Product)
admin.site.register(Currency)
admin.site.register(Delivery)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Promocode)