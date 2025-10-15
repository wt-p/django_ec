from django import forms
from .models import Product, Category
import magic


# class CustomClearableFileInput(ClearableFileInput):
#     initial_text = ''
#     clear_checkbox_label = ''


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label='カテゴリーを選択してください',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Product
        fields = ('name', 'category', 'price', 'sku', 'sale', 'sale_price', 'stock', 'description', 'image')
        error_messages = {
            'name': {
                'required': '商品名を入力してください',
                'max_length': '商品名は%(limit_value)d文字以内で入力してください',
            },
            'category': {
                'required': 'カテゴリーを選択してください',
            },
            'price': {
                'required': '価格を入力してください',
                'invalid': '価格は数値で入力してください',
                'max_digits': '価格は%(max)s桁未満で設定してください',
                'decimal_places': '価格は%(places)s円よりも高く設定してください',
            },
            'sku': {
                'required': '商品管理番号を入力してください',
                'max_length': '商品管理番号は15文字以内で入力してください',
                'unique': 'この商品管理番号はすでに登録されています',
            },
            'sale_price': {
                'invalid': 'セール価格は数値で入力してください',
                'max_digits': 'セール価格は%(max)s桁未満で設定してください',
            },
            'stock': {
                'required': '在庫数を入力してください',
                'invalid': '在庫数は数値で入力してください',
            },
            'description': {
                'max_length': '商品説明は%(limit_value)d文字以内で入力してください',
            },
            'image': {
                'invalid_image': '有効な画像を選択してください',
            },

        }
        labels = {
            'name': '商品名',
            'category': 'カテゴリー',
            'price': '価格',
            'sku': '商品管理番号',
            'sale': 'セール',
            'sale_price': 'セール価格',
            'stock': '在庫数',
            'description': '商品説明',
            'image': '画像',
        }
        help_texts = {
            'sku': '例: PRODUCT-0000001',
            'sale': 'セールを実施する場合はこちらをチェックし、セール価格を入力してください'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        mime = magic.from_buffer(image.read(), mime=True)
        image.seek(0)
        valid_mime_types = ['image/jpeg', 'image/png']

        if mime not in valid_mime_types:
            raise forms.ValidationError('画像形式が不正です。jpegまたはpng形式の画像のみアップロード可能です。')

        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('画像サイズは5MB以内にしてください')

        return image

    # セールにまつわるバリデーション
    def clean(self):
        cleaned = super().clean()
        price = cleaned.get('price')
        sale = cleaned.get('sale')
        sale_price = cleaned.get('sale_price')

        # セールにチェックが入っていないのに、セール価格を入力している場合
        if not sale and sale_price:
            self.add_error('sale', 'セール価格を設定する場合はセールにチェックを入れてください')

        # セールにチェックを入れている場合
        if sale:
            # セール価格を入力していない
            if not sale_price:
                self.add_error('sale_price', 'セール価格を入力してください')
        # セール価格は入力しているが、価格よりも安くない場合
            elif price and sale_price >= price:
                self.add_error('sale_price', 'セール価格は通常価格よりも安く設定してください')
        return cleaned
