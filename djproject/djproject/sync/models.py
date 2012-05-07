#!/usr/bin/env python
# coding=utf-8

"""
ユーザー認証関連
"""

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class SnsAccount(models.Model):
    """
    SNS情報
    """

    # オーナーユーザー
    owner = models.ForeignKey(User)

    # 認証キー等
    facebook_access_token = models.CharField("facebook access token", max_length=255)
    twitter_access_key = models.CharField("twitter access key", max_length=255)
    twitter_access_secret= models.CharField("twitter access secret", max_length=255)

    # 除外クライアント。カンマ区切りで格納する。
    except_twitter_clients = models.CharField(u"除外クライアント", max_length=255)

    # 同期開始日。基本的にcreate_atと同じ
    start_at = models.DateTimeField(u"同期開始日時", auto_now=False, auto_now_add=True)

    # 作成日
    create_at = models.DateTimeField(u"作成日時", auto_now=False, auto_now_add=True)
    # 更新日
    update_at = models.DateTimeField(u"更新日時", auto_now=True, auto_now_add=True)

    # 削除フラグ
    deleted = models.BooleanField(u"削除フラグ")

class SyncedTweet(models.Model):
    """
    同期済みツイート
    """

    owner = models.ForeignKey(SnsAccount)

    tweet = models.CharField(u"tweet ID", max_length=128, unique=True)

    create_at = models.DateTimeField(u"作成日時", auto_now=False, auto_now_add=True)
    update_at = models.DateTimeField(u"更新日時", auto_now=True, auto_now_add=True)

    deleted = models.BooleanField(u"削除フラグ")


#
# admin
#

admin.site.register(SnsAccount, admin.ModelAdmin)
admin.site.register(SyncedTweet, admin.ModelAdmin)

# EOF

