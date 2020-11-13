from .base import *

DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'digital_reputation',
        # TODO: WARNING need change
        'PASSWORD': 'password',
    }
}
