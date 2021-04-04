from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api import serializers
from rest_framework import permissions
from accounts.models import CustomUser


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