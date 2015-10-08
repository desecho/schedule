# Django local settings for movies_project project.

LOCAL_SETTINGS = True
from settings import *

import os
import django

ADMINS = (
    ('Anton Samarchyan', 'desecho@gmail.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',           # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'schedule',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': 'denorm',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                               # Set to empty string for default.
    }
}

DJANGO_DIR = os.path.dirname(os.path.realpath(django.__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    DJANGO_DIR + '/contrib/admin/static',
    BASE_DIR + '/static'
)

MIDDLEWARE_CLASSES += (
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'chromelogger.DjangoMiddleware',
)


INSTALLED_APPS += (
    'django_extensions',
    #'debug_toolbar',
)


INTERNAL_IPS = ('192.168.0.107',)
