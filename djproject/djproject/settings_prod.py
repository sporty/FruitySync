#!/usr/bin/env python
# coding:utf-8

from djproject.settings_common import *


# smiletechnology.jp
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
        'HOST': "mysqlinstance.ckoq5hf60pxi.ap-northeast-1.rds.amazonaws.com",
        'PORT': '3306',
    }
}

deploy_url = "http://fsync.smiletechnology.jp"

# Twitterアプリ情報
TWITTER_CONSUMER_KEY = "RJvS8LyHvqH1ITOq3qOxg"
TWITTER_CONSUMER_SECRET = "TcA11JcJwM1JSr2tRhlJgQDDKlInqEDFblsuMmUdfs"
TWITTER_REDIRECT_URL = deploy_url+"/sync/twitter-oauth-callback/"

# Facebookアプリ情報
FACEBOOK_APP_ID = "450798718264073"
FACEBOOK_APP_SECRET = "40e97b01a0d76603804c4535b7b9f138"
FACEBOOK_REDIRECT_URL = deploy_url+"/sync/facebook-oauth-callback/"

# EOF
