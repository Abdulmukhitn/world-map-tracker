# map_tracker/settings.py

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Ensure WhiteNoise is configured
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Keep only this allauth middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_-i3!w8(opp#bk38&dj*@@&ep_($)30!a3yd$ay=r!lown#n%*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
    'rest_framework',
    'allauth',  # Remove duplicates
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    
    # Custom apps
    'countries',
    'users',
    'ai_guide',
]
SITE_ID = 1
AUTHENTICATION_BACKENDS = [  # Fixed typo in AUTHENTICATION_BACKENDS
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'map_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'map_tracker.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Login URL
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'users:login'  # Updated to use namespaced URL

# Social Auth Configuration
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_SECRET', ''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'APP': {
            'client_id': os.getenv('FACEBOOK_CLIENT_ID', ''),
            'secret': os.getenv('FACEBOOK_SECRET', ''),
            'key': ''
        },
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time',
        ],
    }
}

# django-allauth settings
ACCOUNT_LOGIN_METHODS = {'email'}  # Replaces ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Replaces ACCOUNT_EMAIL_REQUIRED and ACCOUNT_USERNAME_REQUIRED
ACCOUNT_RATE_LIMITS = {
    'login_failed': {'attempts': 5, 'timeout': 300}  # Replaces ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT
}
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
SOCIALACCOUNT_AUTO_SIGNUP = True

# Remove these deprecated settings:
# ACCOUNT_EMAIL_REQUIRED
# ACCOUNT_AUTHENTICATION_METHOD
# ACCOUNT_USERNAME_REQUIRED
# ACCOUNT_LOGIN_ATTEMPTS_LIMIT
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT

# Email settings (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Appwrite Configuration
APPWRITE_ENDPOINT = 'https://fra.cloud.appwrite.io/v1'
APPWRITE_PROJECT_ID = '68125b020008f58668cb'
APPWRITE_API_KEY = 'YOUR_API_KEY'

# Add CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://fra.cloud.appwrite.io",
    "https://world-map-tracker-gnda.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://fra.cloud.appwrite.io",
    "https://world-map-tracker-gnda.onrender.com",
]