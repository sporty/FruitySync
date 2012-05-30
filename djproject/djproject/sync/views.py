#!/usr/bin/env python
# coding=utf-8

"""
ユーザー認証
"""
import os
import urllib
import cgi
import pprint
pp = pprint.PrettyPrinter(indent=4)

import tweepy
import facebook

from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.conf import settings

from models import SnsAccount, SyncedTweet
from forms import SignupForm

import djproject.core.fb as fb


@login_required
def twitter_oauth_callback(request):
    """
    認証の後に飛んでくるコールバックURL。アプリの設定画面で定義されている。
    """
    twitter_request_token_key = request.session.get('twitter_request_token_key', None)
    twitter_request_token_secret = request.session.get('twitter_request_token_secret', None)

    request_token_key = request.GET.get("oauth_token")
    request_verifier  = request.GET.get('oauth_verifier')

    if not request_token_key == twitter_request_token_key:
        return u"リクエストトークンが異なっています"

    auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

    auth.set_request_token(twitter_request_token_key, twitter_request_token_secret)
    access_token = auth.get_access_token(request_verifier)

    # access_tokenをsessionに保存
    request.session['twitter_access_key'] = access_token.key
    request.session['twitter_access_secret'] = access_token.secret

    return HttpResponseRedirect(reverse('sync-twitter-signup', args=[]))

@login_required
def twitter_oauth(request):
    """
    twitterの認証を行う
    """

    '''
    twitter_consumer_key = raw_input('Consumer key: ').strip()
    twitter_consumer_secret = raw_input('Consumer secret: ').strip()
    '''

    env="web"
    if env == "cli":
        # リダイレクトではなく、pinによる簡易認証
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

        # Open authorization URL in browser
        webbrowser.open(auth.get_authorization_url())
        # Ask user for verifier pin
        pin = raw_input('Verification pin number from twitter.com: ').strip()

        # Get access token
        token = auth.get_access_token(verifier=pin)

        twitter_access_key = token.key
        twitter_access_secret = token.secret
    else:
        # ウェブアプリではリダイレクト。第３引数でURLを指定可能
        auth = tweepy.OAuthHandler(
                        settings.TWITTER_CONSUMER_KEY, 
                        settings.TWITTER_CONSUMER_SECRET,
                        callback=settings.TWITTER_REDIRECT_URL,
                    )
        # 認証URLを決定
        redirect_url = auth.get_authorization_url()
        # request_tokenを保存
        request.session['twitter_request_token_key'] = auth.request_token.key
        request.session['twitter_request_token_secret'] = auth.request_token.secret

        return HttpResponseRedirect(redirect_url)

    '''
    # Give user the access token
    print 'Access token:'
    print '  Key: %s' % token.key
    print '  Secret: %s' % token.secret
    '''

def facebook_oauth_callback(request):
    """
    facebookの認証コールバック
    """

    verification_code = request.GET.get("code", None)
    if not verification_code:
        raise FacebookAuthError(u"codeがありません")
    print verification_code

    args = dict(
                client_id=settings.FACEBOOK_APP_ID,
                redirect_uri=settings.FACEBOOK_REDIRECT_URL
            )
    args["client_secret"] = settings.FACEBOOK_APP_SECRET
    args["code"] = verification_code
    access_token_connection = urllib.urlopen(
        settings.FB_AUTH_BASE + "access_token?" + urllib.urlencode(args)
    )
    access_token_raw = access_token_connection.read()
    response = cgi.parse_qs(access_token_raw)
    print response
    access_token = response["access_token"][-1]

    request.session['facebook_access_key'] = access_token

    return HttpResponseRedirect(reverse('sync-signup', args=[]))

def facebook_oauth(request):
    """
    facebookの認証を行う
    """

    # 権限の設定
    perms = [
            'email', # 
            'user_status', # 
            'read_stream', # feedの読み込み
            'user_photos', # 非公開アルバムの閲覧
            'status_update', 
            'publish_stream' # ウォールへの書き込み
            ]
    args = dict(
                client_id=settings.FACEBOOK_APP_ID, 
                redirect_uri=settings.FACEBOOK_REDIRECT_URL,
                scope=','.join(perms)
            )
    return HttpResponseRedirect(
                settings.FB_AUTH_BASE + "authorize?" +
                urllib.urlencode(args)
            )

@login_required
def twitter_signup(request):
    """
    twitter情報を保存
    """
    # twitter認証が済んでいない場合は認証ページにリダイレクト
    twitter_access_key = request.session.get('twitter_access_key', None)
    twitter_access_secret = request.session.get('twitter_access_secret', None)
    if not twitter_access_key or not twitter_access_secret:
        return HttpResponseRedirect(reverse('sync-twitter-oauth', args=[]))

    # account情報を取得
    account = SnsAccount.objects.get(owner=request.user)

    # 保存する。
    account.twitter_access_key = twitter_access_key
    account.twitter_access_secret = twitter_access_secret
    account.save()

    return HttpResponseRedirect(reverse('sync-index', args=[]))

def signup(request):
    """
    facebookでユーザー登録を行う。
    """

    # ログイン済みの場合はトップページに戻る
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('sync-index', args=[]))

    # facebook認証が済んでいない場合は認証ページにリダイレクト
    facebook_access_key = request.session.get('facebook_access_key', None)
    if not facebook_access_key:
        return HttpResponseRedirect(reverse('sync-facebook-oauth', args=[]))

    print "signup."

    # ユーザーを追加する
    if request.method == "POST":
        print "post."
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(email, email, password)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            # ログインしてしまう

            login_user = authenticate(username=email, password=password)
            if login_user is not None:
                if login_user.is_active:
                    login(request, login_user)

            account = SnsAccount()
            account.owner = user
            account.facebook_access_token = facebook_access_key
            account.save()

            return HttpResponseRedirect(reverse('sync-index', args=[]))
        else:
            # もう一度フォームを表示
            return render_to_response('sync/signup.html',
                        {
                            "page_title": u"ユーザー登録",
                            "form": form,
                        },
                        context_instance=RequestContext(request))

    print "form."
    # 情報をフォームに表示
    graph = facebook.GraphAPI(facebook_access_key)

    # facebookから情報を取得
    profile = graph.get_object("me")
    print "profile "+"-"*50
    pp.pprint(profile)
    form = SignupForm({
        "email": profile["email"],
        "first_name": profile["first_name"],
        "last_name": profile["last_name"],
        })

    return render_to_response('sync/signup.html',
                {
                    "page_title": u"ユーザー登録",
                    "form": form,
                },
                context_instance=RequestContext(request))

@login_required
def sync(request):
    """
    矯正同期
    """
    account = SnsAccount.objects.get(owner=request.user)
    account.sync()

    return HttpResponseRedirect(reverse('sync-index', args=[]))

def index(request):
    """
    トップページ
    """
    return render_to_response('sync/index.html',
                {
                    "page_title": u"ユーザー情報",
                },
                context_instance=RequestContext(request))


# EOF
