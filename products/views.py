from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product


class ProductList(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductDetail(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    # 自分以外の最新の商品を4件、related_products としてテンプレートに渡す処理
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = (Product.objects.exclude(pk=self.object.pk).order_by('-created_at')[:4])
        return context
