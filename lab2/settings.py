"""Изолированная БД и обычное хранилище статики только для лабораторных тестов."""
from myproject.settings import *

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'null': {'class': 'logging.NullHandler'}},
           'loggers': {'django.request': {'handlers': ['null'], 'propagate': False}}}
