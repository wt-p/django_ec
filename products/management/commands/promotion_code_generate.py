import random
import string
from django.core.management.base import BaseCommand
from products.models import PromoCode


class Command(BaseCommand):
    help = "ランダムな7桁英数字のプロモーションコードを10個生成するコマンド"

    def handle(self, *args, **options):
        # コードの長さ
        length = 7
        # 生成するコードの数
        num_of_code = 10
        # コードの文字列（英数字）
        chars = string.ascii_uppercase + string.digits
        # DBにある既存のコードを格納
        existing_codes = set(PromoCode.objects.values_list('promo_code', flat=True))
        promo_list = []
        # ループ内の重複チェック用
        new_generated_codes = set()

        self.stdout.write("コード生成を開始します...")

        while len(promo_list) < num_of_code:
            new_code = ''.join(random.choices(chars, k=length))

            # すでに今回生成済みでないか、すでにDBに登録のあるコードでないかチェック
            if new_code not in new_generated_codes and new_code not in existing_codes:
                promo_list.append(PromoCode(
                    promo_code=new_code,
                    discount_amount=random.randint(100, 1000)
                ))
                new_generated_codes.add(new_code)

        PromoCode.objects.bulk_create(promo_list)

        self.stdout.write(self.style.SUCCESS(f'{num_of_code}個のプロモコードを生成しました'))
