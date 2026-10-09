"""
Django settings for scrapsaathi project.
Production-grade configuration with Prometheus metrics, structured logging,
PostgreSQL support with SQLite fallback, CORS, and DRF JWT integration.
"""

from pathlib import Path
import os
from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-scrapsaathi-production-grade-key-nk-securities-dev')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,testserver').split(',') if h.strip()]
APPEND_SLASH = False

# Application definition
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'django_prometheus',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Local Domain Apps
    'common',
    'authentication',
    'users',
    'rates',
    'pickups',
    'collector',
    'donations',
    'contact',
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.middleware.RequestContextMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'scrapsaathi.urls'

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

WSGI_APPLICATION = 'scrapsaathi.wsgi.application'
ASGI_APPLICATION = 'scrapsaathi.asgi.application'

# Database Configuration: PostgreSQL by default, with automatic fallback for local test/dev
DATABASE_URL = os.getenv('DATABASE_URL', '')
DB_ENGINE = os.getenv('DB_ENGINE', 'postgresql').lower()
USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'scrapsaathi_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'scrapsaathi_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'scrapsaathi_password')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

if DATABASE_URL:
    try:
        parsed_db = urlparse(DATABASE_URL)
        if parsed_db.scheme.startswith('postgres'):
            POSTGRES_DB = parsed_db.path.lstrip('/')
            POSTGRES_USER = parsed_db.username or POSTGRES_USER
            POSTGRES_PASSWORD = unquote(parsed_db.password or '') if parsed_db.password else POSTGRES_PASSWORD
            POSTGRES_HOST = parsed_db.hostname or POSTGRES_HOST
            POSTGRES_PORT = str(parsed_db.port or POSTGRES_PORT)
            DB_ENGINE = 'postgresql'
    except Exception:
        pass

use_postgres = False
if not USE_SQLITE and DB_ENGINE != 'sqlite':
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            connect_timeout=2,
        )
        conn.close()
        use_postgres = True
    except Exception:
        use_postgres = False

if use_postgres:
    DATABASES = {
        'default': {
            'ENGINE': 'django_prometheus.db.backends.postgresql',
            'NAME': POSTGRES_DB,
            'USER': POSTGRES_USER,
            'PASSWORD': POSTGRES_PASSWORD,
            'HOST': POSTGRES_HOST,
            'PORT': POSTGRES_PORT,
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django_prometheus.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'common.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    'PAGE_SIZE': 10,
}

# CORS Configuration
raw_origins = os.getenv('CLIENT_ORIGINS', os.getenv('CORS_ALLOWED_ORIGINS', ''))
default_client_origins = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
    'https://scrap-sathi.vercel.app',
    'https://scrap-sathi-lyart.vercel.app',
    'https://scrap-sathi-amankum2004s-projects.vercel.app',
    'https://scrap-sathi-git-main-amankum2004s-projects.vercel.app',
]
if raw_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in raw_origins.split(',') if o.strip()]
else:
    CORS_ALLOWED_ORIGINS = default_client_origins

CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True').lower() in ('true', '1', 't')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# JWT & Security Secrets
JWT_SECRET = os.getenv('JWT_SECRET', 'supersecret-scrapsaathi-jwt-secret-key-nk-securities')
JWT_EXPIRES_IN = int(os.getenv('JWT_EXPIRES_IN', '86400'))
OTP_EXPIRATION_SECONDS = int(os.getenv('OTP_EXPIRATION_SECONDS', '600'))
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', os.getenv('VITE_GOOGLE_CLIENT_ID', ''))

# Email & SMTP Settings
EMAIL_HOST = os.getenv('SMTP_HOST', os.getenv('EMAIL_HOST', 'smtp.gmail.com'))
EMAIL_PORT = int(os.getenv('SMTP_PORT', os.getenv('EMAIL_PORT', '587')))
EMAIL_HOST_USER = os.getenv('PRIMARY_EMAIL', os.getenv('EMAIL', os.getenv('EMAIL_HOST_USER', '')))
EMAIL_HOST_PASSWORD = os.getenv('PRIMARY_EMAIL_PASSWORD', os.getenv('PASSWORD', os.getenv('EMAIL_HOST_PASSWORD', '')))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend' if EMAIL_HOST_PASSWORD else 'django.core.mail.backends.console.EmailBackend'
)
DEFAULT_FROM_EMAIL = f"{os.getenv('EMAIL_FROM_NAME', 'ScrapSaathi')} <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else 'noreply@scrapsaathi.com'

# Cloudinary Integration (Image Uploads)
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')

# Rate Limiting Configuration
RATE_LIMIT_WINDOW_MS = int(os.getenv('RATE_LIMIT_WINDOW_MS', '900000'))
RATE_LIMIT_MAX = int(os.getenv('RATE_LIMIT_MAX', '100'))
AUTH_RATE_LIMIT_MAX = int(os.getenv('AUTH_RATE_LIMIT_MAX', '10'))
OTP_RATE_LIMIT_MAX = int(os.getenv('OTP_RATE_LIMIT_MAX', '5'))

# Admin Seed / Initial Setup Credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@scrapsaathi.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@123456')
ADMIN_NAME = os.getenv('ADMIN_NAME', 'System Administrator')
ADMIN_PHONE = os.getenv('ADMIN_PHONE', '9876543210')

# Structured Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'structured': {
            'format': '[{asctime}] {levelname} [{name}] [req:{request_id}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] {levelname} [{name}] {message}',
            'style': '{',
        },
    },
    'filters': {
        'request_id': {
            '()': 'common.middleware.RequestIdFilter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
            'filters': ['request_id'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'scrapsaathi': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
