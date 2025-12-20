from django.urls import path
from .views import ProductList, ProductDetail


urlpatterns = [
    path('list/', ProductList.as_view(), name='product_list'),
    path('detail/<int:pk>/', ProductDetail.as_view(), name='product_detail')
]
