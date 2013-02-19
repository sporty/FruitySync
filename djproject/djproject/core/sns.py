#/usr/bin/env python
# coding=utf-8

import os
import shutil
import copy
import datetime
import webbrowser
import cgi
import urllib
import urllib2
import json
import random
import re
import random
import tempfile
import logging
logger = logging.getLogger('application')
import pprint
pp = pprint.PrettyPrinter(indent=4)

import tweepy
import facebook

import exceptionhandler as eh


class JST(datetime.tzinfo):
    def utcoffset(self,dt):
        return datetime.timedelta(hours=9)
    def dst(self,dt):
        return datetime.timedelta(0)
    def tzname(self,dt):
        return "JST"

class PostEntity(object):
    """
    """

# SnsのAPIを扱うクラス

class SnsAdapter(object):
    """
    """

    def set_auth(self):
        """
        認証情報を設定
        """
        pass

    def __init__(self):
        """
        """
        pass

class TwitterAdapter(SnsAdapter):
    """
    """

    def get_profile(self):
        """
        """
        api = self.get_api()

        me = api.me() # 自身のUserクラス取得
        return me

    def get_screen_name(self):
        """
        """
        profile = self.get_profile()
        return profile.screen_name

    def get_api(self):
        """
        """
        # twitter api
        auth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_secret)
        auth.set_access_token(self.twitter_access_key, self.twitter_access_secret)
        return tweepy.API(auth_handler=auth)

    def set_auth(self,
            twitter_consumer_key, twitter_consumer_secret,
            twitter_access_key, twitter_access_secret
            ):
        """
        認証情報を設定
        """
        self.twitter_consumer_key = twitter_consumer_key
        self.twitter_consumer_secret = twitter_consumer_secret
        self.twitter_access_key = twitter_access_key
        self.twitter_access_secret = twitter_access_secret

    def _get_action_link(self):
        """
        """
        # twitterアカウントへのリンク
        screen_name = self.get_screen_name()
        action_name = u"@%s on Twitter" % (screen_name, )
        action_link = u"https://twitter.com/#!/%s" % (screen_name, )
        action = json.dumps({u'name': action_name, u'link': action_link})
        return action

    def find_status(self, since_id, since_datetime, except_ids, except_clients=None, check_all_status=False):
        """
        tweetからfacebookのwallにかきこむstatusを取得する

        @param since_id 最後に同期したID
        @param except_ids list 除外tweetIDのリスト
        @param except_clients list 除外clientのリスト
        @param check_all_status

        @return list 
        """
        if not self.twitter_consumer_key or not self.twitter_consumer_secret or not self.twitter_access_key or not self.twitter_access_secret:
            raise eh.TwitterAuthError(u"twitterの認証を行ってください")

        # twitter api
        auth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_secret)
        auth.set_access_token(self.twitter_access_key, self.twitter_access_secret)
        api = tweepy.API(auth_handler=auth)

        # tweetを取得しながらpostすべきstatusを整理。新しい順に評価する。
        result = []

        for status in tweepy.Cursor(api.user_timeline, count=32000, include_entities='true', since_id=since_id).items(32000):
            # idが既に書き込み済みなら、終了。これ以上前のツイートは既に反映済みとする。
            if str(status.id) in except_ids:
                if check_all_status:
                    continue
                else:
                    break
            # 除外クライアントならスキップ
            if status.source in except_clients:
                continue
            # 開始日時以前ならスキップ
            ca = copy.copy(status.created_at)
            delta = datetime.timedelta(hours=9)
            #ca = ca.replace(tzinfo=JST()) # timezoneをJSTに変更
            if since_datetime and ca < since_datetime-delta:
                continue
            # @関連
            if len(status.entities['user_mentions']):
                continue

            post_type = "wall"
            message = status.text
            photo_filenames = []

            #tweet = u"%s %d %s %s" % (status.created_at, status.id, status.author.name, status.text)

            # mediaがある場合は画像がアップロードされている
            if 'media' in status.entities.keys():
                post_type = "photo"
                for media in status.entities['media']:
                    # テキストからリンクを削除する
                    #message = '%s [%f]' % (message, random.random(), )
                    message = message.replace(media['url'], u"")

                    # テキストが無いとエラーになるので全角スペースでも入れておく
                    if not message:
                        message = u"　"

                    # 画像をダウンロードする
                    download_url = media['media_url_https']
                    request = urllib2.Request(download_url)
                    response = urllib2.urlopen(request)

                    filename = os.path.join(self.TEMPORARY_DIR,
                            os.path.basename(download_url))
                    with file(filename, "w") as fp:
                        fp.write(response.read())
                    photo_filenames.append(filename)

            """
            if 'urls' in status.entities.keys():
                for url in status.entities['urls']:
                    contents = urllib.urlopen(url)

            # ツイートに写真のリンクが含まれていた場合はダウンロードし、photoにアップロード
            m = re.findall(ur"(http://[a-zA-Z0-9._\-/%&?]+)", message)
            for link in m:
                '''
                contents = urllib.urlopen(link)
                '''
            """

            action = self._get_action_link()

            post = dict(
                    type=post_type, 
                    id=status.id, 
                    message=message, 
                    photos=photo_filenames, 
                    date=status.created_at,
                    action=action,
                    source=status.source
                    )

            result.append(post)

        # 順番を古い順にする
        result.reverse()

        return result

    def __del__(self):
        # 一時ファイル置き場を削除

        shutil.rmtree(self.TEMPORARY_DIR)

    def __init__(self,
            twitter_consumer_key=None, twitter_consumer_secret=None,
            twitter_access_key=None, twitter_access_secret=None
            ):
        """
        コンストラクター
        """
    
        # 一時ファイル置き場を作成
        self.TEMPORARY_DIR = tempfile.mkdtemp()
        logger.debug('make temporary directory : '+self.TEMPORARY_DIR)

        if twitter_consumer_key and twitter_consumer_secret and twitter_access_key and twitter_access_secret:
            self.set_auth(
                twitter_consumer_key, twitter_consumer_secret,
                twitter_access_key, twitter_access_secret
            )

class FacebookAdapter(SnsAdapter):
    """
    facebook api を使ってfacebook情報にアクセス
    """

    def put_feed(self, message, action=None):
        """
        """
        graph = self.get_api()
        graph.put_object("me", "feed", message=message.encode('utf-8'), actions=action)

    def put_photo(self, message, photo_filename, album_id=None, action=None):
        """
        """
        graph = self.get_api()
        graph.put_photo(file(str(photo_filename)), message=message.encode('utf-8'), album_id=album_id, actions=action)

    def post_wall(self, posts, album_id):
        """
        ウォールに投稿する。

        @param posts リスト
        @param album_id 写真をアップロードするアルバムID
        @return 反映したtweetIDリスト
        """
        self._last_posts = []

        for post in posts:
            id = post['id']
            post_type = post['type']
            message = post['message']
            photos = post['photos']
            action = post['action']

            try:
                if post_type == "wall":
                    self.put_feed(message, action)
                elif post_type == "photo":
                    for photo in photos:
                        if os.path.isfile(photo):
                            self.put_photo(message, photo, album_id, action)
                        else:
                            raise eh.ApiError(u"写真が無いよ [%s]" % (photo, ))
                else:
                    pass
            except facebook.GraphAPIError, e:
                if e == "(#506) Duplicate status message":
                    # 同一投稿ブロック
                    print u"同じメッセージ書き込めないエラー"
                elif e == "(#341) Feed action request limit reached":
                    # 連続と浮こうブロック
                    print u"書き込い過ぎエラー"
                else:
                    print e
                raise eh.ApiError(e)

            self._last_posts.append(id)

        return self._last_posts

    def get_last_posts(self):
        """
        """

        return self._last_posts

    def get_profile(self):
        """
        """
        graph = self.get_api()

        profile = graph.get_object("me")
        return profile

    def get_friends(self):
        """
        """
        graph = self.get_api()

        friends = graph.get_connections("me", "friends")
        return friends

    def get_wall_photo_id(self, album_name=None):
        """
        アルバムのIDを取得。
        album_nameが指定されていた場合は名前で検索、
        その他はwallタイプのアルバムを検索する

        @param album_name アルバム名unicode文字列
        @return string アルバムID文字列
        """

        # アルバムか「ウォールの写真」のIDを取得
        album_id = None
        albums = self.get_albums()
        for album in albums['data']:
            #Wall photoという名前のアルバムは二つ存在するがtypeがwallの方ならアップロード可能
            if album_name and anbum_name == album['name']:
                album_id = str(album['id'])
                break
            elif album['type'] == "wall":
                album_id = str(album['id'])
                break

        return album_id

    def get_albums(self):
        """
        """
        graph = self.get_api()

        albums = graph.get_object("me/albums")
        return albums

    def get_feeds(self):
        """
        """
        graph = self.get_api()

        feeds = graph.get_object("me/feed")
        return feeds

    def get_api(self):
        """
        """

        graph = facebook.GraphAPI(self.facebook_access_key)
        return graph

    def set_auth(self, facebook_access_key):
        """
        認証情報を設定
        """
        self.facebook_access_key = facebook_access_key

    def __init__(self, facebook_access_key=None):
        """
        コンストラクター
        """
    
        if facebook_access_key:
            self.set_auth(facebook_access_key)


class FacebookWall(object):
    """
    facebookウォールに他のSNSからの書き込みを同期する
    """

    def sync_twitter(self, since_id=None, since_datetime=None, except_ids=[], except_clients=[], album_name=None, check_all_status=False, dry=False):
        """
        twitterからfacebookに同期

        @param since_id 最後に同期したID
        @param since_datetime 同期開始の日時
        @param except_ids list 除外tweetIDのリスト
        @param except_clients list 除外clientのリスト
        @param album_name unicode 写真を投稿するアルバムの名前。Noneの場合はWall photos
        @param check_all_status 反映済みIDを見つけた時点で終了しない
        @param dry dry-run

        @return 反映したtweetIDリスト
        """

        # 同期するステータスを整理して取得
        posts = self._twitter.find_status(since_id, since_datetime, except_ids, except_clients, check_all_status)

        # wall_photo
        album_id = self._facebook.get_wall_photo_id(album_name)

        #facebookに書き込み 
        if not dry:
            try:
                result = self._facebook.post_wall(posts, album_id)
            except:
                raise

            return result

        return []

    def set_twitter_auth(self,
            twitter_consumer_key, twitter_consumer_secret,
            twitter_access_key, twitter_access_secret
            ):
        """
        twitter認証情報を設定
        """
        self._twitter = TwitterAdapter(
                                twitter_consumer_key,
                                twitter_consumer_secret,
                                twitter_access_key,
                                twitter_access_secret
                            )

    def __init__(self, facebook_access_key):
        """
        コンストラクタ
        """
        self._twitter = None
        self._facebook = FacebookAdapter(facebook_access_key)


if __name__ == "__main__":
    facebook_access_key = "AAAENEM1tKR4BAIrhcww1unZCoWqId0kCnAazM5QstBufHdGtKEca2I0zHUym0DEkWeXIpNN5p4mMO6xCGfkRQedLaAwoGxiF2oHrqqAZDZD"

    TWITTER_CONSUMER_KEY = "26k3546ZenMk1AiXAKfg"
    TWITTER_CONSUMER_SECRET = "vOmH5kcZofAHy01cGH3VTxkItHKheKNonm6BB5IBhiQ"
    twitter_access_key = "567942112-Zwh7PUGMkUb4yCK69XLPzhCB54ZXOgIItPvi0fPu"
    twitter_access_secret = "CQfJcxLXUmhx2jAaaeLg52IhuZwVKL8CcbVn9EBV7Q"

    fb_wall = FacebookWall(facebook_access_key)
    fb_wall.set_twitter_auth(
            TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
            twitter_access_key, twitter_access_secret
            )

    #fb_wall.put_feed(unicode(random.random())*10)

    feeds = fb_wall.get_feeds()
    print "feeds "+"-"*50
    pp.pprint(feeds)

    '''
    fb_wall.sync_twitter()
    '''


# EOF
