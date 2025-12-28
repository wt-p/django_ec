"""
ローカル環境用設定
"""


from .base import *

environ.Env.read_env(env_file=str(BASE_DIR) + '/.env')

SECRET_KEY = env('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db(),
}

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')

# 開発環境はターミナル（docker logs）にメール内容を出力
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
