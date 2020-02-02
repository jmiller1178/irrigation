import os
from utils.logging_filters import skip_suspicious_operations
from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


SASS_PROCESSOR_INCLUDE_DIRS = (
    os.path.join(PROJECT_ROOT, 'sass'),
)
SASS_PROCESSOR_ENABLED = True
COMPRESS_ENABLED = True
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#va$&%c7om&k5=hemp$)@#l%(9-ki#f-(==la6tu(@5kp)1m@$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.125', '192.168.1.126','192.168.1.127',]

INTERNAL_IPS = [
    '127.0.0.1',
    '192.168.1.125',
]

STATIC_URL = '/static/'

RABBITMQ_HOST = "localhost"
RABBITMQ_USERNAME = "webstomp"
RABBITMQ_PASSWORD = "webstomp"
RABBITMQ_WS_PORT = "15674"
DEFAULT_AMQ_TOPIC = 'amq.topic'

# Application definition

INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'django_extensions',
    'sprinklesmart',
    'rest_framework',
    'debug_toolbar',
    'compressor',
    'sass_processor',
    'sekizai',  # for JavaScript and CSS management
    'rabbitmq',
    
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'irrigation.urls'

WSGI_APPLICATION = 'irrigation.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'db/irrigation_rpi3.db'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
SITE_ID = 1
TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'sass_processor.finders.CssFinder'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                 'sekizai.context_processors.sekizai',
            ],
        },
    },
]
INTERNET_CHECK_URL = 'http://www.yahoo.com'

WEATHER_URL = "https://weather-ydn-yql.media.yahoo.com/forecastrss"
WEATHER_APP_ID = 'RM92pQ50'
WEATHER_CONSUMER_KEY = 'dj0yJmk9YWxGUmNERE8yY3ZPJmQ9WVdrOVVrMDVNbkJSTlRBbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWZk'
WEATHER_CONSUMER_SECRET = '10f18a7036102224a29c5a8c9404920ae5594311'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        # Define filter
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filters': ['skip_suspicious_operations'],
            'filename': '/var/www/data/irrigation/log/django.log'
        }
    },
    'loggers': {
        'sprinklesmart': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 'sprinklesmart': {
        #     'handlers': ['file'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
        'sprinklesmart.management':{
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    }
}
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

try:
    from irrigation.local_settings import *
except ImportError:
    pass