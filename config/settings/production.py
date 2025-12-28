"""
本番環境用設定
"""


from .base import *
import os


SECRET_KEY = env('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com']

DATABASES = {
    'default': env.db(),
}

STORAGES['default'] = {
    'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET')
}

# 本番環境はresendを使用
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'resend'
# HerokuのConfig Varsから読み込み
EMAIL_HOST_PASSWORD = os.environ.get('RESEND_API_KEY')
