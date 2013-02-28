#!/usr/bin/env python
# coding:utf-8

from djproject.settings_common import *


# MBA-4.local
DEBUG = True

# URL prefix for static files.
STATIC_URL = '/static/'

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
TWITTER_CONSUMER_KEY = "JnliV6hmrYYND2BdEe3PQ"
TWITTER_CONSUMER_SECRET = "asuJ0jSnfFvioTMqzSzPJMaLz0f0NPCAFtDv4lsEOl0"
TWITTER_REDIRECT_URL = "http://127.0.0.1:8000/sync/twitter-oauth-callback/"

# Facebookアプリ情報
FACEBOOK_APP_ID = "416167055143877"
FACEBOOK_APP_SECRET = "160a403e46c11268d5c4ff07469d6915"
FACEBOOK_REDIRECT_URL = "http://127.0.0.1:8000/sync/facebook-oauth-callback/"

# EOF
