from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.authentication import SessionAuthentication

from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api import serializers
from rest_framework import permissions, viewsets
from accounts.models import CustomUser
from product.models import *
from django.contrib.sessions.models import Session
from product import services


@api_view(['POST'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([permissions.IsAuthenticated,])
def connect_tg(request, format=None):
    content = {}
    try:
        id_tg = int(request.POST.get('id_tg'))
    except ValueError:
        id_tg = None
    if not id_tg:
        content = {'error':{'msg':'ID TG указан неверно'},}
    else:
        user = CustomUser.objects.get(id = request.user.id)
        user.id_tg = id_tg
        user.save()
        content = {'success': {'msg': 'Аккаунт подключен'},}
    return Response(content)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated, ])
def close_session(request, format=None):
    session_key = request.POST.get('session_key')
    content = {}
    try: 
        user_session = Session.objects.get(session_key = session_key)
        user_session_info = user_session.get_decoded()
        if str(request.user.id) == user_session_info.get('_auth_user_id'):
            user_session.delete()
            content['success'] = 'session close'
        else:
            content['error'] = 'user unautentificated'
    except Session.DoesNotExist:
        content['error'] = 'session key not found'
    
    return Response(content)
     

class TokenAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        context = {}
        user = request.user
        token, create_token = Token.objects.get_or_create(user = user)
        if not create_token:
            token.delete()
            token = Token.objects.create(user=user)
        serializer = serializers.TokenSerializer(token)
        context['success'] = serializer.data
        return Response(context)


class MatrixAPI(APIView):
    authentication_classes = [SessionAuthentication]

    def get(self, request, format=None):
        context = {}
        all_matrix = PriceMatrix.objects.all()
        serializer = serializers.MatrixSerializer(all_matrix, many=True)
        context['success'] = serializer.data
        return Response(context)

    
class Basket(APIView):

    def get_object(self, data):
        try:
            return BasketItem.objects.get(**data)
        except BasketItem.DoesNotExist:
            raise Http404
    

    def get_objects(self, data):
        return BasketItem.objects.filter(**data)
    
    def get_basket(self, user):
        return BasketItem.objects.filter(user=user)


    def get(self, request, format=None):
        context = {}
        data = request.GET
        show_all = request.user.has_perm('product.show_all_basket')
        if data.get('user_id') and show_all:
            try: 
                user = CustomUser.objects.get(id = data.get('user_id'))
            except CustomUser.DoesNotExist:
                user = request.user
            basket = self.get_basket(user)
        else:
            basket = self.get_basket(request.user)
        serializer = serializers.BasketSerializer(basket, many=True)
        context['success'] = serializer.data
        return Response(context)


    def post(self, request, format=None):
        context = {}
        data_request = request.POST
        data = {}
        product_id = data_request.get('id')
        data['qty'] = data_request.get('cnt', 1)
        try:
            product = Product.objects.get(id = product_id)
            data['product'] = product.id
            data['user'] = request.user.id
            data['price'] = product.price
        except Product.DoesNotExist:
            error = 'Product not found'
        serializer = serializers.BasketSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            get_basket = self.get_basket(request.user)
            serializer = serializers.BasketSerializer(get_basket, many=True)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

        
    def put(self, request, format=None):
        context = {}
        data_request = request.POST
        data = {}
        snippet = self.get_object({
            'user':request.user.id,
            'product':data_request.get('id')
        })
        data['qty'] = data_request.get('cnt', 1)
        serializer = serializers.BasketSerializer(snippet, data = data, partial=True)
        if serializer.is_valid():
            serializer.save()
            context['success'] = serializer.data
            return Response(context)
        else:
            return Response(serializer.errors)
    

    def delete(self, request, format=None):
        context = {}
        data_request = request.POST
        data = {}
        data['user'] = request.user.id
        data['product'] = data_request.get('id')
        if data['product']:
            item = self.get_object(data)
        else:
            data.pop('product')
            item = self.get_objects(data)
        item.delete()
        get_basket = self.get_basket(request.user)
        serializer = serializers.BasketSerializer(get_basket, many=True)
        context['success'] = serializer.data

        return Response(context)



class ProductAPI(APIView):

    def get(self, request, format=None):
        filter_attr = request.GET
        filter_product = services.ProductServices.filter_product(filter_attr)
        product = Product.objects.filter(**filter_product)
        serializer = serializers.ProductSerializer(product, many=True)
        context = {'success':serializer.data}
        return Response(context)