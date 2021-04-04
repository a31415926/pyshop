from api import views
from django.urls import path


urlpatterns = [
    path('connect_tg/', views.connect_tg),
    path('test_token/', views.TokenAPI.as_view(), name='get_token'),
]