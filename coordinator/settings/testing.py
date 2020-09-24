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
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'coordinator.middleware.Auth0AuthenticationMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

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
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination' +
                                '.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework'
                                '.DjangoFilterBackend',)
}

WSGI_APPLICATION = 'coordinator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PG_NAME', 'test'),
        'USER': os.environ.get('PG_USER', 'postgres'),
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
        'DEFAULT_TIMEOUT': 30,
        'SSL': os.environ.get('REDIS_SSL', False),
    },
    'health_checks': {
        'HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'PORT': os.environ.get('REDIS_PORT', 6379),
        'DB': 0,
        'DEFAULT_TIMEOUT': 30,
        'SSL': os.environ.get('REDIS_SSL', False),
    }
}

redis_pass = os.environ.get('REDIS_PASS', False)
if redis_pass:
    RQ_QUEUES['default']['PASSWORD'] = redis_pass
    RQ_QUEUES['health_checks']['PASSWORD'] = redis_pass

if DEBUG or TESTING:
    RQ_QUEUES['default']['ASYNC'] = True


EGO = {
    'default': {
        'CLIENT_ID': os.environ.get('EGO_CLIENT_ID', 'test-client'),
        'SECRET': os.environ.get('EGO_SECRET', 'test-secret'),
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
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "kids-first.auth0.com")
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

SNS_ARN = None

DATASERVICE_URL = 'http://dataservice'

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
EGO_API = 'http://ego'
DATASERVICE_API = os.environ.get('DATASERVICE_URL', None)

# Timeouts in seconds
TASK_TIMEOUT = 600
RELEASE_TIMEOUT = 3600
REQUEST_TIMEOUT = 0.1
REQUESTS_HEADERS = {
    "User-Agent": "ReleaseCoordinator/testing (python-requests)"
}
