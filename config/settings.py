from pathlib import Path
from datetime import timedelta
import environ
import redis
import os
from firebase_admin import initialize_app, credentials

cred = credentials.Certificate('media/bepro-dd75c-firebase-adminsdk-rwbfr-f449f576e8.json')

initialize_app(cred)

#FIREBASE_APP = initialize_app()

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gf%sh-rp#&qk9j(va0tgkd!ypc&4ayd-$r3&h2&3ja3@wbiiwi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

AUTH_USER_MODEL = 'auth_user.User'
# Application definition

DEFAULT_APPS = [
    'modeltranslation', # 3rd party app
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'fcm_django',
    'django_filters',
    'django_db_logger',
    'django_celery_beat',
    'django_celery_results',
    'imagekit',
    'rest_framework_simplejwt.token_blacklist',
    'after_response'
]

LOCAL_APPS = [
    'utils',
    'auth_user.apps.AuthUserConfig',
    'applications.apps.ApplicationsConfig',
    'companies.apps.CompaniesConfig',
    'scores.apps.ScoresConfig',
    'bepro_statistics.apps.BeproStatisticsConfig',
    'timesheet.apps.TimesheetConfig',
    'tariffs.apps.TariffsConfig',
    'tests.apps.TestsConfig',
    'app_version.apps.AppVersionConfig',
    'notifications.apps.NotificationsConfig',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']


ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'utils.paginator.PagePagination',
    'DEFAULT_METADATA_CLASS': 'rest_framework_json_api.metadata.JSONAPIMetadata',
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'PAGE_SIZE': 25
}

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT')
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        },
        'django.request': {  # logging 500 errors to database
            'handlers': ['db_log'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

CORS_ALLOWED_ORIGIN_REGEXES = env.list('CORS_ALLOWED_ORIGIN_REGEXES')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')
CORS_ALLOW_ALL_ORIGINS = True

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_PATH')
MEDIA_ROOT = env('MEDIA_PATH')
MEDIA_URL = '/media/'

STATICFILES_DIRS = ['static']

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG,
}



FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
     # default: _('FCM Django')
    "APP_VERBOSE_NAME": "bepro.kz",
     # true if you want to have only one active device per registered user at a time
     # default: False
    "ONE_DEVICE_PER_USER": False,
     # devices to which notifications cannot be sent,
     # are deleted upon receiving error response from FCM
     # default: False
    "DELETE_INACTIVE_DEVICES": False,
    # Transform create of an existing Device (based on registration id) into
                # an update. See the section
    # "Update of device with duplicate registration ID" for more details.
    # default: False
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

GOOGLE_APPLICATION_CREDENTIALS=env('CREDENTIALS')


CURRENT_SITE = env('CURRENT_SITE')


CELERY_TIMEZONE = "Asia/Almaty"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

try:
    ACCESS_TOKEN_LIFETIME_DAYS = env('ACCESS_TOKEN_LIFETIME_DAYS')
    ACCESS_TOKEN_LIFETIME_MINUTES = env('ACCESS_TOKEN_LIFETIME_MINUTES')
    ACCESS_TOKEN_LIFETIME = timedelta(days=int(ACCESS_TOKEN_LIFETIME_DAYS), minutes=int(ACCESS_TOKEN_LIFETIME_MINUTES))

    REFRESH_TOKEN_LIFETIME_DAYS = env('REFRESH_TOKEN_LIFETIME_DAYS')
    REFRESH_TOKEN_LIFETIME_MINUTES = env('REFRESH_TOKEN_LIFETIME_MINUTES')
    REFRESH_TOKEN_LIFETIME = timedelta(days=int(REFRESH_TOKEN_LIFETIME_DAYS), minutes=int(REFRESH_TOKEN_LIFETIME_MINUTES))
except:
    ACCESS_TOKEN_LIFETIME = timedelta(days=30)
    REFRESH_TOKEN_LIFETIME = timedelta(days=900)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': ACCESS_TOKEN_LIFETIME,
    'REFRESH_TOKEN_LIFETIME': REFRESH_TOKEN_LIFETIME,
}

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russian')),
    ('kk', gettext('Kazakh')),
    ('en', gettext('English')),

)


MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale')
]