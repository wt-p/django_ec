from django.views.generic import ListView
from .models import Cart, CartItem, Product, OrderItem, PromoCode
from .forms import OrderForm
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


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

        # テンプレートで {{ form }} が使えるようにフォームを追加
        context['form'] = OrderForm()

        cart_items = context[self.context_object_name]
        original_total_price = sum(item.subtotal for item in cart_items)
        applied_promo, discount, total_price = get_promo_details_and_final_price(
            self.request, original_total_price
        )
        context['discount'] = discount
        context['applied_promo'] = applied_promo
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


def get_promo_details_and_final_price(request, cart_total_price):
    promo_id = request.session.get('applied_promo_id')
    applied_promo_code = None
    discount = 0
    discounted_total = cart_total_price

    if promo_id:
        applied_promo_code = PromoCode.objects.filter(id=promo_id, is_used=False).first()
        if applied_promo_code:
            discount = applied_promo_code.discount_amount
            discounted_total = applied_promo_code.apply_discount(cart_total_price)
        else:
            # sessionに入っているのは本来有効なpromo_idにも関わらず、DBに有効なコードがない不整合状態のため、削除
            request.session.pop('applied_promo_id', None)

    return applied_promo_code, discount, discounted_total


def apply_promo(request):
    if request.method != 'POST':
        return redirect('cart_list')

    code = request.POST.get('promo_code')
    promo_code = PromoCode.find_valid_code(code)

    if promo_code and promo_code.is_valid:
        request.session['applied_promo_id'] = promo_code.id
        messages.success(request, f'プロモーションコード「{code}」を適用しました')
    else:
        messages.error(request, '無効なプロモーションコードです')

    return redirect('cart_list')


def checkout(request):
    if request.method != 'POST':
        return redirect('cart_list')

    form = OrderForm(request.POST)
    # カートを取得
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    applied_promo, discount, total_price = get_promo_details_and_final_price(request, cart.total_price)

    if not form.is_valid():
        # これを渡さないとカートとフォームの入力値が空になる
        context = {
            'cart_items': cart.items.all() if cart else [],
            'total_price': total_price,
            'discount': discount,
            'applied_promo': applied_promo,
            'form': form,
        }
        return render(request, 'cart.html', context)

    # ここから下は「POSTかつバリデーション成功」の正常系

    if not cart or cart.is_empty:
        messages.error(request, 'カートに商品が入っていません')
        return redirect('product_list')

    # 注文確定処理
    try:
        with transaction.atomic():
            # 注文を保存
            order = form.save(commit=False)
            order.total_price = total_price
            order.discount_amount = discount
            order.save()

            # 明細を作成し、在庫を減らす
            for item in cart.items.all():
                product = item.product
                # 在庫チェック
                if product.stock < item.quantity:
                    raise ValueError(f'{product.name}の在庫が足りません')

                # 在庫を減らして保存
                product.stock -= item.quantity
                product.save()

                # 注文明細を保存
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name_at_purchase=product.name,
                    price_at_purchase=product.sale_price if product.sale else product.price,
                    quantity=item.quantity
                )

            if applied_promo:
                applied_promo.is_used = True
                applied_promo.used_at = timezone.now()
                applied_promo.save()
                request.session.pop('applied_promo_id', None)

            # カートを空にする
            cart.items.all().delete()

        # メール送信処理
        try:
            context = {
                'order': order,
                'order_items': order.order_items.all()
            }

            subject = f'【Daily Select】ご注文ありがとうございます（注文番号： #{order.id}）'
            message_txt = render_to_string('mail/order_success.txt', context)
            message_html = render_to_string('mail/order_success.html', context)

            send_mail(
                subject,
                message_txt,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                # html_message=は省略不可
                html_message=message_html,
            )
        except Exception as e:
            logger.error(f'Failed to send mail: {e}')

        messages.success(request, '購入ありがとうございます')
        return redirect('product_list')

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart_list')
