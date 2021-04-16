from rest_framework import serializers
from accounts.models import *
from product.models import *
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['user_id', 'key']


class MatrixItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceMatrixItem
        fields = ['id','min_value', 'max_value', 'type_item', 'value']


class MatrixSerializer(serializers.ModelSerializer):
    items = MatrixItemSerializer(source='pricematrixitem_set', many = True)
    class Meta:
        model = PriceMatrix
        fields = ['id', 'name', 'items']