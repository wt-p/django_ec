from django import forms
from .models import Product, Category, Order, PromoCode
from datetime import datetime
import magic
import re


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


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'last_name', 'first_name', 'email', 'tel',
            'zip_code', 'address', 'address2',
            'cc_name', 'cc_number', 'cc_expiration', 'cc_cvv2'
        )

        error_messages = {
            'last_name': {
                'required': '姓は必須です',
            },
            'first_name': {
                'required': '名は必須です',
            },
            'email': {
                'required': 'メールアドレスは必須です',
                'invalid': '有効なメールアドレスを正しく入力してください',
            },
            'tel': {
                'required': '電話番号は必須です',
            },
            'zip_code': {
                'required': '郵便番号は必須です',
            },
            'address': {
                'required': '住所は必須です',
            },
            'cc_name': {
                'required': 'カード名義人は必須です',
            },
            'cc_number': {
                'required': 'カード番号は必須です',
            },
            'cc_expiration': {
                'required': '有効期限（月/年）は必須です',
            },
            'cc_cvv2': {
                'required': 'CVV2は必須です',
            },
        }

        labels = {
            'last_name': '姓',
            'first_name': '名',
            'email': 'メールアドレス',
            'tel': '電話番号（半角数字のみ）',
            'zip_code': '郵便番号',
            'address': '住所',
            'address2': '建物名・部屋番号（任意）',
            'cc_name': 'カード名義人',
            'cc_number': 'カード番号',
            'cc_expiration': '有効期限（月/年）',
            'cc_cvv2': 'CVV2',
        }

        help_texts = {
            'tel': 'ハイフンなしの半角数字で入力してください',
            'cc_name': 'カードに記載されているフルネーム',
            'cc_expiration': '例: 12/28 (月/年)',
            'cc_cvv2': '裏面の3〜4桁の番号'
        }

        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '山田'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '太郎'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'tel': forms.TextInput(attrs={
                'class': 'form-control', 'type': 'tel', 'pattern': r'\d*',
                'maxlength': '11', 'placeholder': '09012345678'
            }),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1000001', 'maxlength': '7'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '東京都千代田区...'}),
            'address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '〇〇マンション 101号室'}),
            'cc_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TARO YAMADA'}),
            'cc_number': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': '12345678901234',
                                                'maxlength': '19'
                                                }),
            'cc_expiration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12/34',
                'maxlength': '5',
                'id': 'cc-expiration'
            }),
            'cc_cvv2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '567', 'maxlength': '4'}),
        }

    # 電話番号のバリデーション
    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if not re.match(r'^\d{10,11}$', tel):
            raise forms.ValidationError('電話番号はハイフンなしの10桁または11桁の数字で入力してください')
        return tel

    # 郵便番号のバリデーション
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if not re.match(r'^\d{7}$', zip_code):
            raise forms.ValidationError('郵便番号はハイフンなしの7桁の数字で入力してください')
        return zip_code

    # カード番号のバリデーション
    def clean_cc_number(self):
        cc_number = self.cleaned_data.get('cc_number')
        if not re.match(r'^\d{14,19}$', cc_number):
            raise forms.ValidationError('有効なカード番号（14〜19桁）を数字で入力してください')
        return cc_number

    # カード有効期限のバリデーション
    def clean_cc_expiration(self):
        expiration = self.cleaned_data.get('cc_expiration')

        # 形式チェック
        if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', expiration):
            raise forms.ValidationError('有効期限は月/年（MM/YY）の形式で正しく入力してください')

        # 有効期限チェック
        month, year = map(int, expiration.split('/'))
        year += 2000
        current = datetime.now()
        if year < current.year or (year == current.year and month < current.month):
            raise forms.ValidationError('有効期限が切れています')

        return expiration

    # cvv2の形式チェック
    def clean_cc_cvv2(self):
        cvv2 = self.cleaned_data.get('cc_cvv2')
        if not re.match(r'^\d{3,4}$', cvv2):
            raise forms.ValidationError('セキュリティコードは3桁または4桁の数字で入力してください')
        return cvv2
