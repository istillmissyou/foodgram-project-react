import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', default='pekw_osrt)3tze%@ci=6t4d(#+n4ki(=odwnr280)=m&p61i-k')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'djoser',
    'recipes',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

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

WSGI_APPLICATION = 'foodgram.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', default='postgres'),
        'USER': os.getenv('POSTGRES_USER', default='postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='my_key_for_test'),
        'HOST': os.getenv('DB_HOST', default='db'),
        'PORT': os.getenv('DB_PORT', default='5432'),
    }
}


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

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'recipes.User'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':
    ['rest_framework.authentication.TokenAuthentication', ],

    'DEFAULT_PERMISSION_CLASSES':
    ['rest_framework.permissions.IsAuthenticatedOrReadOnly', ],

    'DEFAULT_FILTER_BACKENDS':
    ['django_filters.rest_framework.DjangoFilterBackend', ],

    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'recipe': ('api.permissions.AuthorStaffOrReadOnly,',),
        'recipe_list': ('api.permissions.AuthorStaffOrReadOnly',),
        'user': ('api.permissions.OwnerUserOrReadOnly',),
        'user_list': ('api.permissions.OwnerUserOrReadOnly',),
    },
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'user_list': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserSerializer',
    },
}

MAX_LEN_RECIPES_CHARFIELD = 200
MAX_LEN_USERS_CHARFIELD = 120
MIN_LEN_USERNAME = 3
DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'
TRUE_SEARCH = ('1', 'true',)
FALSE_SEARCH = ('0', 'false',)
INGREDIENTS_MIN_AMOUNT = 1
INGREDIENTS_MIN_AMOUNT_ERROR = ('Количество ингредиента не может быть меньше {min_amount}')
