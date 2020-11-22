from .base import *

DEBUG = True

DOMAIN_NAME = "http://127.0.0.1/"

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
