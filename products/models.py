from django.db import models
from django.core.validators import MaxValueValidator


# categoryを使った機能は後ほど拡張予定
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    # categoryを使った機能は後ほど拡張予定
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(max_digits=7, decimal_places=0)
    sku = models.CharField(max_length=15, unique=True)
    sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=7, decimal_places=0, blank=True, null=True)
    stock = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(99)])
    description = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return self.stock > 0  # type: ignore
