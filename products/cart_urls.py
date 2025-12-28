from django.urls import path
from .cart_views import CartItemList, add_to_cart, delete_cart_item, checkout


urlpatterns = [
    path('list/', CartItemList.as_view(), name='cart_list'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('delete/<int:pk>/', delete_cart_item, name='cart_item_delete'),
    path('checkout/', checkout, name='checkout'),
]
