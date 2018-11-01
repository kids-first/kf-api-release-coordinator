"""
Test settings
"""

import os
import uuid

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = str(uuid.uuid4())

DEBUG = True

ALLOWED_HOSTS = []
APPEND_SLASH = False


# Application definition

INSTALLED_APPS = [
    'coordinator.api.apps.ApiConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'drf_yasg'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

ROOT_URLCONF = 'coordinator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
}

WSGI_APPLICATION = 'coordinator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PG_NAME', 'test'),
        'USER': os.environ.get('PG_USER','postgres'),
        'PASSWORD': os.environ.get('PG_PASS', None),
        'HOST': os.environ.get('PG_HOST', '127.0.0.1'),
        'PORT': os.environ.get('PG_PORT', '5432'),
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'PORT': os.environ.get('REDIS_PORT', 6379),
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
    'health_checks': {
        'HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'PORT': os.environ.get('REDIS_PORT', 6379),
        'DB': 0,
        'DEFAULT_TIMEOUT': 30,
    },
}

if DEBUG or TESTING:
    RQ_QUEUES['default']['ASYNC'] = True

EGO = {
    'default': {
        'CLIENT_ID': os.environ.get('EGO_CLIENT_ID', 'test-client'),
        'SECRET': os.environ.get('EGO_SECRET', 'test-secret'),
    }
}

SNS_ARN = None

DATASERVICE_URL = 'http://dataservice'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

# APIs
EGO_API = 'http://ego'
DATASERVICE_API = os.environ.get('DATASERVICE_URL', None)

# Timeouts in seconds
TASK_TIMEOUT = 600
RELEASE_TIMEOUT = 3600
REQUEST_TIMEOUT = 0.1
