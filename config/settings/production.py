"""
本番環境用設定
"""


from .base import *


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
