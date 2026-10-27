from pathlib import Path
import os
import dj_database_url

# Базовый путь к проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТЬ ДЛЯ ДЕПЛОЯ ---
# Включаем DEBUG локально, но отключаем в продакшене, если переменная задана
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Секретный ключ (локально берется дефолтный, на Render задай свой в переменные окружения)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-local-development-key-change-me')

# Разрешенные хосты (локальные + домен на Render)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']


# --- ПРИЛОЖЕНИЯ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Твои приложения
    'main',
    
    # Если ты используешь REST Framework для API (установи через pip install djangorestframework)
    # 'rest_framework', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Для раздачи статики на Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Общая папка шаблонов, если есть
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.cart_total',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# --- РАЗДЕЛЕНИЕ БАЗ ДАННЫХ (БЕЗ ПОТЕРЬ ЛОКАЛЬНО) ---
# Если на Render задан DATABASE_URL, используем Postgres. Локально — твой SQLite.
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- ВАЛИДАЦИЯ ПАРОЛЕЙ ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- ЯЗЫК И ВРЕМЯ (МИНСК) ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Minsk'
USE_I18N = True
USE_TZ = True


# --- СТАТИКА И МЕДИА (КАРТИНКИ) ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Для картинок новостей и товаров
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Хранилище для статики в продакшене (WhiteNoise оптимизирует файлы)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- ПОДДЕРЖКА РАЗНОГО УРОВНЯ ЛОГИРОВАНИЯ ---
# Локально в консоли можно смотреть детальный DEBUG
LOGGING_LEVEL = os.getenv('DJANGO_LOGGING_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
    },
}



"""
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # Читать API могут все (GET), изменять (POST, PUT, DELETE) — только авторизованные
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]
}
"""

