from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'digital_reputation',
        # TODO: WARNING need change
        'PASSWORD': 'password',
    }
}
