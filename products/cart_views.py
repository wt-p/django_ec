from django.views.generic import ListView
from .models import Cart, CartItem, Product
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


class CartItemList(ListView):
    model = CartItem
    template_name = 'cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        if not self.request.session.session_key:
            self.request.session.create()
        session_key = self.request.session.session_key
        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            return CartItem.objects.none()
        return CartItem.objects.filter(cart=cart).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = context[self.context_object_name]
        total_price = sum(item.subtotal for item in cart_items)
        context['total_price'] = total_price
        return context


def add_to_cart(request, product_id):
    # 1. リダイレクト先の決定 (一覧に戻るか、詳細に戻るか)
    referer_url = request.META.get('HTTP_REFERER')

    if referer_url:
        # 前のページ（参照元）がある場合は、そのURLに戻る
        redirect_url = referer_url
    else:
        # 参照元が取れない場合は、商品一覧（'product_list'）に戻る
        redirect_url = 'product_list'

    if request.method != 'POST':
        messages.error(request, '無効な操作です。')
        return redirect(redirect_url)

    # 2. セッションとカートの準備
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)

    product = get_object_or_404(Product, pk=product_id)

    # 3. 数量の取得 (詳細画面からの指定に対応)
    try:
        # 詳細画面からの追加はquantity、一覧からの場合は1
        quantity_to_add = int(request.POST.get('quantity', 1))
        if quantity_to_add <= 0:
            messages.error(request, '数量は1以上を指定してください')
            return redirect(redirect_url)
    except ValueError:
        messages.error(request, '数量は半角数字で入力してください')
        return redirect(redirect_url)

    # 4. 在庫チェック
    if product.stock <= 0:
        messages.error(request, f'{product.name} は在庫切れです')
        return redirect(redirect_url)

    # 5. カートアイテムの取得または作成
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        # 新規追加時も「0 + 追加数」で計算できるよう初期値を 0 にする
        defaults={'quantity': 0}
    )

    # 6. 合計数量が在庫を超えないかチェック
    target_quantity = item.quantity + quantity_to_add
    if target_quantity > product.stock:
        messages.error(request, f'{product.name} の在庫数（{product.stock}個）を超えたためカートに追加できませんでした')
        return redirect(redirect_url)

    # 7. 保存
    item.quantity = target_quantity
    item.save()

    messages.success(request, f'{product.name} をカートに追加しました')
    return redirect(redirect_url)


def delete_cart_item(request, pk):
    item = get_object_or_404(CartItem, pk=pk)

    session_key = request.session.session_key
    if item.cart.session_key != session_key:
        messages.error(request, '不正な操作です')
        return redirect('cart_list')

    product_name = item.product.name
    item.delete()

    messages.success(request, f'{product_name} をカートから削除しました')
    return redirect('cart_list')
