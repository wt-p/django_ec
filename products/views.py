from django.views.generic import ListView, DetailView
from .models import Product, Cart


class CartCountMixin:
    """
    他ビューで共通してカート内の商品数を取得するためのMixin。
    ヘッダーのカートアイコン等に数字を表示するために使用する。
    """
    def get_cart_count(self):
        session_key = self.request.session.session_key
        if not session_key:
            return 0
        try:
            cart = Cart.objects.get(session_key=session_key)
            return cart.items.count()
        # カートが未作成（まだ何も追加していない）ユーザーでも
        # エラーを出さず「0」として処理を続行させるため
        except Cart.DoesNotExist:
            return 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 共通の処理として cart_count をコンテキストに追加
        context['cart_count'] = self.get_cart_count()
        return context


class ProductList(CartCountMixin, ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'


class ProductDetail(CartCountMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    # 自分以外の最新の商品を4件、related_products としてテンプレートに渡す処理
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = (Product.objects.exclude(pk=self.object.pk).order_by('-created_at')[:4])
        return context
