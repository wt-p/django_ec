from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# categoryを使った機能は後ほど拡張予定
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50,)
    # categoryを使った機能は後ほど拡張予定
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        validators=[MinValueValidator(1, message='価格は1円以上で設定してください')]
    )
    sku = models.CharField(max_length=15, unique=True)
    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(
        max_digits=7,
        decimal_places=0,
        validators=[MinValueValidator(1, message='セール価格は1円以上で設定してください')],
        blank=True,
        null=True
    )
    stock = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(99, message='在庫数は99個以内で設定してください')
        ]
    )
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='products/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0  # type: ignore


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def is_empty(self):
        return not self.items.exists()

    def __str__(self):
        return self.session_key


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        # セール価格があり、セールを設定している場合はセール価格、違えば通常価格
        price = self.product.price
        if self.product.sale and self.product.sale_price is not None:
            price = self.product.sale_price

        return price * self.quantity

    # 同じカートの中に、同じ商品が2行以上作られないようにする
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_product'
            ),
        ]

    def __str__(self):
        return f"{self.product.name} ({self.quantity}個) in Cart ({self.cart.session_key})"


class Order(models.Model):
    last_name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    tel = models.CharField(max_length=12)
    zip_code = models.CharField(max_length=7)
    address = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250, blank=True)

    # カード情報

    cc_name = models.CharField(max_length=30)
    cc_number = models.CharField(max_length=19)
    # 月/年 (MM/YY)
    cc_expiration = models.CharField(max_length=5)
    # セキュリティコード
    cc_cvv2 = models.CharField(max_length=4)

    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def cc_last_four_number(self):
        # カード番号が~19桁まであるので末尾4桁だけ
        if self.cc_number:
            return str(self.cc_number)[-4:]
        return ""

    def __str__(self):
        return f"Order #{self.id} - {self.last_name} {self.first_name} (¥{self.total_price:,}) - {self.created_at}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # 商品名を変更しても問題ないように注文時の商品名をコピーしておく
    name_at_purchase = models.CharField(max_length=50)
    # 価格変更しても問題ないように注文時の価格をコピーしておく
    price_at_purchase = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        # 購入時の単価での小計
        return self.price_at_purchase * self.quantity

    def __str__(self):
        return f"Order #{self.order.id} | {self.name_at_purchase} x {self.quantity}"
