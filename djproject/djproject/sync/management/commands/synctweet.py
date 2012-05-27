#/usr/bin/env python
# coding=utf-8


from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from djproject.sync.models import SnsAccount, SyncedTweet

import djproject.core.fb as fb


class Command(BaseCommand):
    """
    """

    args = u'<user_id user_id ...>'
    help = u'登録されているアカウントのtweetをfacebookに同期します'

    def handle(self, *args, **options):
        """
        """

        if len(args) > 0:
            print args

        accounts = SnsAccount.objects.all()

        for account in accounts:
            twitter_access_key = account.twitter_access_key
            twitter_access_secret = account.twitter_access_secret
            if not twitter_access_key or not twitter_access_secret:
                raise TwitterAuthError(u"twitterの認証を行ってください")

            facebook_access_key = account.facebook_access_token
            if not facebook_access_key:
                raise FacebookAuthError(u"facebookの認証を行ってください")
            except_clients = account.except_twitter_clients.split(',')
            since_datetime = account.start_at
            print account.update_at

            # 同期
            fb_wall = fb.Wall(facebook_access_key)
            fb_wall.set_twitter_auth(
                    settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET,
                    twitter_access_key, twitter_access_secret
                    )
            synced = SyncedTweet.objects.filter(owner=account).order_by('-update_at')
            #print synced
            since_id = None
            if len(synced):
                since_id = synced[0].tweet
            except_ids = [ei.tweet for ei in synced]
            try:
                sync_ids = fb_wall.sync_twitter(since_id, since_datetime, except_ids, except_clients, None, True)
                print sync_ids
            except:
                raise

            # SyncedTweetに登録
            for id in sync_ids:
                tweet = SyncedTweet()
                tweet.owner = account
                tweet.tweet = id
                tweet.save()

# EOF
