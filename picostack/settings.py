"""
Django settings for picostack project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-9@)*p*&1hk+6$2ura%9m8pf(sdz@us4p4!y%zq(#0meck2t+o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'picostack.vms',
    'bootstrap3',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'picostack.urls'

WSGI_APPLICATION = 'picostack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Use as location for the database file.
DATABASE_LOCATION = '/var/picostack/db/picostk.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_LOCATION,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

SETTINGS_PATH = os.path.normpath(os.path.dirname(__file__))
# Find templates in the same folder as settings.py.
TEMPLATE_DIRS = (
    os.path.join(SETTINGS_PATH, 'templates'),
)
STATICFILES_DIRS = (
    os.path.join(SETTINGS_PATH, 'static'),
)


BOOTSTRAP3 = {
    'jquery_url': STATIC_URL + 'bower_components/jquery/dist/jquery.min.js',
    'base_url': STATIC_URL + 'bower_components/bootstrap/dist/',
    'css_url': None,
    'theme_url': STATIC_URL + 'bower_components/bootstrap/dist/css/bootstrap-theme.min.css',
    'javascript_url': None,
    'horizontal_label_class': 'col-md-2',
    'horizontal_field_class': 'col-md-4',
}
