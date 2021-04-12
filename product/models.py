from django.db import models
from accounts.models import CustomUser
from django.db.models.signals import post_delete
from datetime import date
import os


class Product(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    type_product = models.CharField(choices=[('material', 'Материальный'),('file', 'Файл'),],
        default='material', max_length=100, verbose_name='Тип товара')
    file_digit = models.FileField(default=None, blank=True, null=True, verbose_name='Файл (при тип товара - Файл)')
    title = models.CharField(max_length=300, default='Noname')
    stock = models.IntegerField(blank=True, default=0, null=True)
    brand = models.CharField(blank=True, null=True, max_length=150)
    desc = models.TextField(blank=True, null=True, default='')
    vendor_code = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(default=0, blank=True, null=True)
    old_price = models.FloatField(default=0, blank=True, null=True)
    cid = models.ManyToManyField('Categories', related_name = 'category')
    date_add = models.DateTimeField(auto_now_add=True)
    date_edit = models.DateTimeField(auto_now=True)
    photo = models.FileField(default=None, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.price = round(self.price, 2)
        self.old_price = round(self.old_price, 2)
        super(Product, self).save(*args, **kwargs)
    
    def delete(self):
        self.photo.delete()
        super(Product, self).delete()


class Categories(models.Model):
    name = models.CharField(max_length=250, default='Noname cat', unique=True)
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=15, blank=True)
    rate = models.FloatField(default=1)
    disp = models.CharField(max_length=20, blank=True, null=True, default='y.e.')

    def __str__(self):
        return self.name



class Delivery(models.Model):
    name = models.CharField(max_length=350, default='Delivery')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Promocode(models.Model):
    #table with promocode
    type_discount_choices = [
        ('fixed', 'Фиксированная'),
        ('relative', 'Относительная'),
    ]
    type_promo_choices = [
        ('onceuse', 'Одноразовые'),
        ('reusable', 'Многоразовые'),
    ]
    code = models.CharField(max_length=200, unique=True)
    type_code = models.CharField(default='fixed', choices=type_discount_choices, max_length=50)
    amount_of_discount = models.FloatField(default=0)
    type_promo = models.CharField(default='reusable', choices=type_promo_choices, max_length=50)
    status = models.BooleanField(default=True)
    start_promo = models.DateField(blank=True, null = True)
    end_promo = models.DateField(blank=True, null = True)

    def __str__(self):
        return self.code

    @classmethod
    def is_promo(cls, promocode):
        is_promo = cls.objects.filter(code = promocode, status = True)[0]
        if is_promo:
            if is_promo.start_promo:
                if is_promo.end_promo:
                    if is_promo.start_promo <= date.today() <= is_promo.end_promo:
                        return True
                else:
                    if is_promo.start_promo <= date.today():
                        return True
            elif is_promo.end_promo:
                if date.today() <= is_promo.end_promo:
                    return True
            else:
                return True
            return False
        return False
    

    @classmethod
    def get_discount(cls, total_sum, promocode):
        promo = cls.objects.get(code=promocode)
        if promo.type_code == 'fixed':
                discount = promo.amount_of_discount
        elif promo.type_code == 'relative':
            discount = total_sum * promo.amount_of_discount / 100
        return discount


class Order(models.Model):
    #user = 
    status_choices = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('processing', 'В обработке'),
        ('finished', 'Завершен'),
        ('cancel', 'Отменен'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True, blank=True)
    full_amount = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    full_amount_on_curr = models.FloatField(default=0)
    total_amount_on_curr = models.FloatField(default=0)
    date_create = models.DateTimeField(auto_now_add=True)
    status = models.CharField(default='new', choices=status_choices, max_length=50)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    rate_currency = models.FloatField(default=1)
    promo = models.ForeignKey(Promocode, on_delete=models.PROTECT, blank=True, null=True, default='')


    class Meta:
        permissions = (('change_status','Can change status order'),)

    @classmethod
    def change_status(cls, id_order, new_status):
        obj = cls.objects.get(pk = id_order)
        obj.status = new_status
        obj.save()

class OrderItem(models.Model):
    #содержимое заказов
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    id_good = models.IntegerField(default=1)
    title_good = models.CharField(default='Noname', max_length=300)
    cost = models.FloatField(default=1)
    cost_on_curr = models.FloatField(default=1)
    qty = models.IntegerField(default=1)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)


class FileTelegram(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    id_file = models.CharField(max_length=100)