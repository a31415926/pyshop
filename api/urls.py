from api import views
from django.urls import path


urlpatterns = [
    path('connect_tg/', views.connect_tg),
    path('close_session/', views.close_session),
    path('test_token/', views.TokenAPI.as_view(), name='get_token'),
    path('get_matrix/', views.MatrixAPI.as_view(), name = 'get_matrix'),
    path('shop/basket', views.Basket.as_view(), name = 'api_basket'),
    path('shop/product', views.ProductAPI.as_view()),
]