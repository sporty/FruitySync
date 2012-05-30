#!/usr/bin/env python
# coding=utf-8

"""
ユーザー認証関連
"""

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings

import djproject.core.fb as fb

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

    def sync(self, is_dry=False):
        """
        同期処理
        """
        twitter_access_key = self.twitter_access_key
        twitter_access_secret = self.twitter_access_secret
        if not twitter_access_key or not twitter_access_secret:
            raise TwitterAuthError(u"twitterの認証を行ってください")

        facebook_access_key = self.facebook_access_token
        if not facebook_access_key:
            raise FacebookAuthError(u"facebookの認証を行ってください")
        except_clients = self.except_twitter_clients.split(',')
        since_datetime = self.start_at
        print self.update_at

        # 同期
        fb_wall = fb.Wall(facebook_access_key)
        fb_wall.set_twitter_auth(
                settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET,
                twitter_access_key, twitter_access_secret
                )
        synced = SyncedTweet.objects.filter(owner=self).order_by('-update_at')
        #print synced
        since_id = None
        if len(synced):
            since_id = synced[0].tweet
        except_ids = [ei.tweet for ei in synced]
        try:
            sync_ids = fb_wall.sync_twitter(since_id, since_datetime, except_ids, except_clients, None, True, is_dry)
            print sync_ids
        except:
            raise

        # SyncedTweetに登録
        for id in sync_ids:
            try:
                tweet = SyncedTweet()
                tweet.owner = self
                tweet.tweet = id
                tweet.save()
            except:
                raise

    def __unicode__(self):
        return u'%s %s' % (self.owner.first_name, self.owner.last_name)

    class Meta():
        verbose_name = u"Snsアカウント情報"
        verbose_name_plural = u"Snsアカウント情報"


class SyncedTweet(models.Model):
    """
    同期済みツイート
    """

    owner = models.ForeignKey(SnsAccount)

    tweet = models.CharField(u"tweet ID", max_length=128, unique=True)

    create_at = models.DateTimeField(u"作成日時", auto_now=False, auto_now_add=True)
    update_at = models.DateTimeField(u"更新日時", auto_now=True, auto_now_add=True)

    deleted = models.BooleanField(u"削除フラグ")

    def __unicode__(self):
        return u'%s (%s)' % (self.tweet, self.update_at)

    class Meta():
        verbose_name = u"同期済みTweet ID"
        verbose_name_plural = u"同期済みTweet ID"


#
# admin
#

admin.site.register(SnsAccount, admin.ModelAdmin)
admin.site.register(SyncedTweet, admin.ModelAdmin)

# EOF

