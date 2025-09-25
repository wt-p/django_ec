"""
本番環境用設定
"""


from .base import *


SECRET_KEY = env("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ['.herokuapp.com']

DATABASES = {
    "default": env.db(),
}
