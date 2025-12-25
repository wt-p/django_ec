from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Product, Category, Order
from django.urls import reverse_lazy
from .forms import ProductForm
from django.contrib.messages.views import SuccessMessageMixin


class ManageProductList(ListView):
    model = Product
    template_name = 'manage_product_list.html'
    context_object_name = 'manage_products'


class ManageProductCreate(SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'manage_product_create.html'
    context_object_name = 'manage_categorys'
    success_url = reverse_lazy('manage_product:list')
    success_message = '商品を追加しました'


class ManageProductUpdate(SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'manage_product_edit.html'
    context_object_name = 'manage_product'
    success_url = reverse_lazy('manage_product:list')
    success_message = '商品情報を更新しました'


class ManageProductDelete(SuccessMessageMixin, DeleteView):
    model = Product
    template_name = 'manage_product_delete.html'
    context_object_name = 'manage_product'
    success_url = reverse_lazy('manage_product:list')
    success_message = '商品を削除しました'


class ManageOrderList(ListView):
    model = Order
    template_name = 'manage_order_list.html'
    context_object_name = 'orders'


class ManageOrderDetail(DetailView):
    model = Order
    template_name = 'manage_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.order_items.all()
        return context
