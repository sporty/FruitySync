#/usr/bin/env python
# coding=utf-8

import os
import webbrowser
import cgi
import urllib
import urllib2
import json
import random
import re
import pprint
pp = pprint.PrettyPrinter(indent=4)

import tweepy
import facebook

import exceptionhandler as eh


class PostEntity(object):
    """
    """

class Wall(object):
    """
    facebookウォールに他のSNSからの書き込みを同期する
    """

    def _find_status(self, since, except_ids, except_clients=None, check_all_status=False):
        """
        tweetからfacebookのwallにかきこむstatusを取得する

        @param since datetime.datetime 同期開始日
        @param except_ids list 除外tweetIDのリスト
        @param except_clients list 除外clientのリスト
        @param check_all_status

        @return list 
        """
        if not self.twitter_consumer_key:
            or not self.twitter_consumer_secret:
            or not self.twitter_access_key:
            or not self.twitter_access_secret:
            raise eh.TwitterAuthError(u"twitterの認証を行ってください")

        # twitter api
        auth = tweepy.OAuthHandler(self.twitter_consumer_key, self.twitter_consumer_secret)
        auth.set_access_token(self.twitter_access_key, self.twitter_access_secret)
        api = tweepy.API(auth_handler=auth)

        # tweetを取得しながらpostすべきstatusを整理。新しい順に評価する。
        result = []

        for status in tweepy.Cursor(api.user_timeline, count=32000, include_entities='true').items(32000):
            # idが既に書き込み済みなら、終了。これ以上前のツイートは既に反映済みとする。
            if status.id in except_ids:
                if check_all_status:
                    continue
                else:
                    break
            # 除外クライアントならスキップ
            if status.source in except_clients:
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
                    filename = os.path.basename(download_url)
                    photo_filenames.append(filename)
                    fp = file(filename, "w")
                    fp.write(response.read())
                    fp.close()

            """
            if 'urls' in status.entities.keys():
                for url in status.entities['urls']:
                    print url
                    contents = urllib.urlopen(url)
                    print contents.geturl()
                    print contents.info()

            # ツイートに写真のリンクが含まれていた場合はダウンロードし、photoにアップロード
            m = re.findall(ur"(http://[a-zA-Z0-9._\-/%&?]+)", message)
            for link in m:
                #print link
                '''
                contents = urllib.urlopen(link)
                print contents.geturl()
                print contents.info()
                '''
            """

            post = dict(
                    type=post_type, 
                    id=status.id, 
                    message=message, 
                    photos=photo_filenames, 
                    date=status.created_at
                    )

            result.append(post)

        # 順番を古い順にする
        result.reverse()

        return result

    def get_wall_photo_id(self, album_name=None):
        """
        アルバムのIDを取得。
        album_nameが指定されていた場合は名前で検索、
        その他はwallタイプのアルバムを検索する

        @param album_name アルバム名unicode文字列
        @return string アルバムID文字列
        """
        # facebook api
        graph = facebook.GraphAPI(self.facebook_access_key)

        # アルバムか「ウォールの写真」のIDを取得
        album_id = None
        albums = graph.get_object("me/albums")
        for album in albums['data']:
            #Wall photという名前のアルバムは二つ存在するがtypeがwallの方ならアップロード可能
            if album_name and anbum_name == album['name']:
                album_id = str(album['id'])
                print "find by name."
                print album['id']
                print album['name']
                print album['type']
                break
            elif album['type'] == "wall":
                album_id = str(album['id'])
                print "find by type."
                print album['id']
                print album['name']
                print album['type']
                break

        return album_id

    def _post_wall(self, posts, album_id):
        """
        ウォールに投稿する。

        @param posts リスト
        @param album_id 写真をアップロードするアルバムID
        @return 反映したtweetIDリスト
        """
        result = []

        if not self.facebook_access_key:
            raise eh.FacebookAuthError(u"facebookの認証を行ってください")

        # facebook api
        graph = facebook.GraphAPI(self.facebook_access_key)

        for post in posts:
            print post
            id = post['id']
            post_type = post['type']
            message = post['message']
            photos = post['photos']

            try:
                if post_type == "wall":
                    graph.put_object("me", "feed", message=message.encode('utf-8'))
                elif post_type == "photo":
                    for photo in photos:
                        print photo
                        if os.path.isfile(photo):
                            graph.put_photo(file(str(photo)), message=message.encode('utf-8'), album_id=album_id)
                        else:
                            print u"写真が無いよ"
                else:
                    pass
            except facebook.GraphAPIError, e:
                print e
                # 同一投稿ブロック
                "(#506) Duplicate status message"
                # 連続と浮こうブロック
                "(#341) Feed action request limit reached"
                raise

            result.append(id)

    def sync_twitter(self, since, except_ids, except_clients, album_name=None, check_all_status=False):
        """
        twitterからfacebookに同期

        @param since datetime.datetime 同期開始日
        @param except_ids list 除外tweetIDのリスト
        @param except_clients list 除外clientのリスト
        @param album_name unicode 写真を投稿するアルバムの名前。Noneの場合はWall photos
        @param check_all_status 反映済みIDを見つけた時点で終了しない

        @return 反映したtweetIDリスト
        """

        # wall_photo
        album_id = get_wall_photo_id(album_name)

        # 同期するステータスを整理して取得
        posts = _find_status(since, except_ids, except_clients, check_all_status)

        #facebookに書き込み 
        result = _post_wall(posts)

        return result

    def set_twitter_auth(self,
            twitter_consumer_key, twitter_consumer_secret,
            twitter_access_key, twitter_access_secret
            ):
        """
        twitter認証情報を設定
        """
        self.twitter_consumer_key = twitter_consumer_key
        self.twitter_consumer_secret = twitter_consumer_secret
        self.twitter_access_key = twitter_access_key
        self.twitter_access_secret = twitter_access_secret

    def __init__(self, facebook_access_key):
        """
        コンストラクタ
        """
        self.facebook_access_key = facebook_access_key


if __name__ == "__main__":
    facebook_access_key = "AAAENEM1tKR4BAIrhcww1unZCoWqId0kCnAazM5QstBufHdGtKEca2I0zHUym0DEkWeXIpNN5p4mMO6xCGfkRQedLaAwoGxiF2oHrqqAZDZD"

    TWITTER_CONSUMER_KEY = "26k3546ZenMk1AiXAKfg"
    TWITTER_CONSUMER_SECRET = "vOmH5kcZofAHy01cGH3VTxkItHKheKNonm6BB5IBhiQ"
    twitter_access_key = "567942112-Zwh7PUGMkUb4yCK69XLPzhCB54ZXOgIItPvi0fPu"
    twitter_access_secret = "CQfJcxLXUmhx2jAaaeLg52IhuZwVKL8CcbVn9EBV7Q"

    fb_wall = Wall(facebook_access_key)
    fb_wall.set_twitter_auth(
            TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
            twitter_access_key, twitter_access_secret
            )
    fb_wall.sync_twitter()


# EOF
