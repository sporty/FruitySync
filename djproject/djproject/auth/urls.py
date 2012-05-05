#/usr/bin/env python
# coding=utf-8

from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.index, name="auth-index"),
)

# EOF
