"""
ローカル環境用設定
"""


from .base import *

environ.Env.read_env(env_file=str(BASE_DIR) + "/.env")

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": env.db(),
}

INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')
