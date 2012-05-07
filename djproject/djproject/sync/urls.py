#/usr/bin/env python
# coding=utf-8

from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="sync-index"),
    url(r"^twitter-oauth-callback/$", views.twitter_oauth_callback, name=""),
    url(r"^twitter-oauth/$", views.twitter_oauth, name=""),
    url(r"^facebook-oauth-callback/$", views.facebook_oauth_callback, name=""),
    url(r"^facebook-oauth/$", views.facebook_oauth, name="sync-facebook-oauth"),
    url(r"^signup/$", views.signup, name="sync-signup"),
)

# EOF
