#!/usr/bin/env python
# coding:utf-8

import os
import sys


# Django settings for djproject project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASEDIR = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# データベース情報
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'db_fsync',
        'USER': 'fsync',
        'PASSWORD': 'fsync0623',
        'HOST': "MBA-4.local",
        'PORT': '3306',
    }
}

# Twitterアプリ情報
# アプリごとに用意されているconsumer_keyとconsumer_secret
TWITTER_CONSUMER_KEY = "26k3546ZenMk1AiXAKfg"
TWITTER_CONSUMER_SECRET = "vOmH5kcZofAHy01cGH3VTxkItHKheKNonm6BB5IBhiQ"
TWITTER_REDIRECT_URL = "http://0.0.0.0:5000/sync/twitter-oauth-callback/"

# Facebookアプリ情報
#リダイレクトURLをローカルサーバーにするために、debugモードでは切り替える必要がある
FACEBOOK_APP_ID = "295840793831710"
FACEBOOK_APP_SECRET = "04b0d34d97ba550f6aef4dccb064f4bb"
FACEBOOK_REDIRECT_URL = "http://0.0.0.0:5000/sync/facebook-oauth-callback/"

FB_GRAPH_API_BASE = "https://graph.facebook.com/"
FB_AUTH_BASE = FB_GRAPH_API_BASE+"oauth/"


# deploy先で切り替わる情報
try:
    if "HOSTNAME" in os.environ:
        # dev.smiletechnology.jp
        if os.environ["HOSTNAME"] == "dev.smiletechnology.jp":
            DATABASES['default'].update({
                'NAME': "db_fsync",
                'USER': "fsync",
                'PASSWORD': "fsync0623",
                'HOST': "localhost",
                'PORT': "3306",
            })
            DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'

            DEBUG = False
        elif os.environ["HOSTNAME"] == "smiletechnology.jp":
            DATABASES['default'].update({
                'NAME': "db_fsync",
                'USER': "fsync",
                'PASSWORD': "fsync0623",
                'HOST': "localhost",
                'PORT': "3306",
            })
            DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'

            deploy_url = "http://fsync.smiletechnology.jp"

            # Twitterアプリ情報
            TWITTER_CONSUMER_KEY = "RJvS8LyHvqH1ITOq3qOxg"
            TWITTER_CONSUMER_SECRET = "TcA11JcJwM1JSr2tRhlJgQDDKlInqEDFblsuMmUdfs"
            TWITTER_REDIRECT_URL = deploy_url+"/sync/twitter-oauth-callback/"

            # Facebookアプリ情報
            FACEBOOK_APP_ID = "450798718264073"
            FACEBOOK_APP_SECRET = "40e97b01a0d76603804c4535b7b9f138"
            FACEBOOK_REDIRECT_URL = deploy_url+"/sync/facebook-oauth-callback/"

            # debugモードをoffにする
            DEBUG = False

except Exception:
    print 'Unexpected error:', sys.exc_info()
    raise


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Tokyo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ja'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = ''
STATIC_ROOT = os.path.join(BASEDIR, '..', '..', 'static_root')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASEDIR, '..', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '87y%dfg*-&amp;3fi8-*21&amp;!kls@d8%p&amp;=e7^^i+!cn+5u4i=u70gx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',

    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'djproject.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'djproject.wsgi.application'

TEMPLATE_DIRS = (
    BASEDIR + '/templates',
)

INTERNAL_IPS = ('127.0.0.1', )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'south',
    'gunicorn',
    'debug_toolbar',

    'djproject.sync',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

def custom_show_toolbar(request):
    return False # Always show toolbar, for example purposes only.

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
    'HIDE_DJANGO_SQL': False,
}

# EOF
