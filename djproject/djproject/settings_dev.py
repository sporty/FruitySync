#!/usr/bin/env python
# coding:utf-8

from djproject.settings_common import *


# dev.smiletechnology.jp
DEBUG = False

# URL prefix for static files.
STATIC_URL = '/'

# データベース情報
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'db_fsync',
        'USER': 'fsync',
        'PASSWORD': 'fsync0623',
        'HOST': "localhost",
        'PORT': '3306',
    }
}

deploy_url = "http://fsync.dev.smiletechnology.jp"

# Twitterアプリ情報
TWITTER_CONSUMER_KEY = "26k3546ZenMk1AiXAKfg"
TWITTER_CONSUMER_SECRET = "vOmH5kcZofAHy01cGH3VTxkItHKheKNonm6BB5IBhiQ"
TWITTER_REDIRECT_URL = deploy_url+"/sync/twitter-oauth-callback/"

# Facebookアプリ情報
FACEBOOK_APP_ID = "295840793831710"
FACEBOOK_APP_SECRET = "04b0d34d97ba550f6aef4dccb064f4bb"
FACEBOOK_REDIRECT_URL = deploy_url+"/sync/facebook-oauth-callback/"

# EOF
