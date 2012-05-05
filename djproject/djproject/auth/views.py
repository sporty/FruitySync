#!/usr/bin/env python
# coding=utf-8

"""
ログイン認証
"""

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from django.conf import settings

#from models import User

import facebook

def facebook_current_user(cookies):
    """
    """

    # facebookのログイン情報はクッキーから取得する
    cookie = facebook.get_user_from_cookie(
                                cookies, 
                                settings.FACEBOOK_APP_ID, 
                                settings.FACEBOOK_APP_SECRET)

    # ログインアカウントの保存
    _current_user = None
    if cookie:
        # Store a local instance of the user data so we don't need
        # a round-trip to Facebook on every request
        user = User.get_by_key_name(cookie["uid"])
        if not user:
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")
            user = User(key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"])
            user.put()
        elif user.access_token != cookie["access_token"]:
            user.access_token = cookie["access_token"]
            user.put()
        _current_user = user
    return _current_user

def index(request):
    """
    """
    facebook_user = facebook_current_user(request.COOKIES)

    #return HttpResponse("hello world %s" % (facebook_user.name, ))

    return render_to_response('auth/index.html',
                {
                    'facebook_user': facebook_user,
                    'facebook_app_id': settings.FACEBOOK_APP_ID,
                },
                context_instance=RequestContext(request))

# EOF
