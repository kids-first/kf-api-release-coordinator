"""
Django settings for coordinator project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import uuid

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(uuid.uuid4())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]
APPEND_SLASH = False

RQ_API_TOKEN = os.environ.get('RQ_API_TOKEN', None)


# Application definition

INSTALLED_APPS = [
    'coordinator.api.apps.ApiConfig',
    'coordinator.graphql.apps.GraphQLConfig',
    'coordinator',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'django_rq',
    'drf_yasg',
    'django_fsm',
    'corsheaders',
    'graphene_django'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'coordinator.middleware.Auth0AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_WHITELIST = (
    'kidsfirstdrc.org',
    'kids-first.io',
)

CORS_ORIGIN_REGEX_WHITELIST = (
    r'^(https?:\/\/)?([a-z0-9-]+[.])*kidsfirstdrc\.org$',
    r'^(https?:\/\/)?([a-z0-9-]+[.])*kids-first\.io$',
    r'^(https?:\/\/)?([a-z0-9-]+)*.netlify\.com$',
)

CORS_ALLOW_CREDENTIALS = True

# Assume we're in local environment if there is no vault url
if os.environ.get('VAULT_URL', None) is None:
    CORS_ORIGIN_REGEX_WHITELIST += (r'^(https?:\/\/)?localhost.*$',)

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
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}

WSGI_APPLICATION = 'coordinator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PG_NAME', 'dev'),
        'USER': os.environ.get('PG_USER', 'postgres'),
        'PASSWORD': os.environ.get('PG_PASS', None),
        'HOST': os.environ.get('PG_HOST', '127.0.0.1'),
        'PORT': os.environ.get('PG_PORT', '5432'),
    }
}


# Redis
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
RQ_QUEUES = {
    "default": {
        "HOST": redis_host,
        "PORT": redis_port,
        "DB": 0,
        "DEFAULT_TIMEOUT": 30,
    },
    "health_checks": {
        "HOST": redis_host,
        "PORT": redis_port,
        "DB": 0,
        "DEFAULT_TIMEOUT": 30,
    },
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "{}:{}".format(redis_host, redis_port),
        "OPTIONS": {"DB": 1},
    }
}

redis_pass = os.environ.get('REDIS_PASS', False)
if redis_pass:
    RQ_QUEUES['default']['PASSWORD'] = redis_pass
    RQ_QUEUES['health_checks']['PASSWORD'] = redis_pass
    CACHES["default"]["OPTIONS"]["PASSWORD"] = redis_pass


# EGO oauth creds
EGO = {
    'default': {
        'CLIENT_ID': os.environ.get('EGO_CLIENT_ID', None),
        'SECRET': os.environ.get('EGO_SECRET', None),
    }
}


# API for Ego
EGO_API = os.environ.get('EGO_API', 'https://ego.kids-first.io')
# Cache key for where to rerieve and store the ego signing key
CACHE_EGO_KEY = 'EGO_PUBLIC_KEY'
# Cache key for where to rerieve and store the ego service token
CACHE_EGO_TOKEN = 'EGO_SERVICE_TOKEN'
# How often the Ego public key should be retrieved from ego, 1 day default
CACHE_EGO_TIMEOUT = 86400

# Settings for Auth0
# Store both the public key for verifying incoming requests and a service key
# for attaching to outgoing requests.
# The public key will be fetched after the timeout window has elapsed, but
# the service key will be refetched after it the expiration date included
# in the last access token.
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "https://kids-first.auth0.com")
AUTH0_JWKS = os.environ.get(
    "AUTH0_JWKS", "https://kids-first.auth0.com/.well-known/jwks.json"
)
AUTH0_AUD = os.environ.get(
    "AUTH0_AUD", "https://kf-release-coord.kidsfirstdrc.org"
)
AUTH0_CLIENT = os.environ.get("AUTH0_CLIENT")
AUTH0_SECRET = os.environ.get("AUTH0_SECRET")
CACHE_AUTH0_KEY = os.environ.get("CACHE_AUTH0_KEY", "AUTH0_PUBLIC_KEY")
CACHE_AUTH0_SERVICE_KEY = os.environ.get(
    "CACHE_AUTH0_SERVICE_KEY", "AUTH0_SERVICE_KEY"
)
CACHE_AUTH0_TIMEOUT = int(os.environ.get("CACHE_AUTH0_TIMEOUT", 86400))

JWT_AUD = 'https://kf-release-coord.kidsfirstdrc.org'

SNS_ARN = os.environ.get('SNS_ARN', None)

DATASERVICE_URL = os.environ.get('DATASERVICE_URL', None)

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation' +
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation' +
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation' +
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation' +
        '.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'coordinator.User'

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
    os.path.join(BASE_DIR, '../', 'static')
]

GRAPHENE = {
    'SCHEMA': 'coordinator.graphql.schema.schema'
}

# APIs
EGO_API = os.environ.get('EGO_URL', None)
DATASERVICE_API = os.environ.get('DATASERVICE_URL', None)

# Timeouts in seconds
TASK_TIMEOUT = 160000
RELEASE_TIMEOUT = 360000
REQUEST_TIMEOUT = 15
REQUESTS_HEADERS = {
    "User-Agent": "ReleaseCoordinator/production (python-requests)"
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "[{asctime}] {levelname} {module}: {message}",
            "datefmt": "%H:%M:%S",
            "style": "{"
        },
    },
    "handlers": {
        "rq_console": {
            "level": "INFO",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        }
    },
    'loggers': {
        "rq.worker": {
            "handlers": ["rq_console"],
            "level": "ERROR"
        },
        "coordinator.authentication": {
            "handlers": ["rq_console"],
            "level": "INFO"
        },
        "coordinator.tasks": {
            "handlers": ["rq_console"],
            "level": "INFO"
        },
    }
}
