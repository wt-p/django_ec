from django.urls import path
from .manage_views import ManageProductList, ManageProductCreate, ManageProductUpdate, ManageProductDelete
from basicauth.decorators import basic_auth_required

app_name = "manage_product"


urlpatterns = [
    path('list/', basic_auth_required(ManageProductList.as_view()), name='list'),
    path('create/', basic_auth_required(ManageProductCreate.as_view()), name='create'),
    path('edit/<int:pk>', basic_auth_required(ManageProductUpdate.as_view()), name='edit'),
    path('delete/<int:pk>', basic_auth_required(ManageProductDelete.as_view()), name='delete'),
]
