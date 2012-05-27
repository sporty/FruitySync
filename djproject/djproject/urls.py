#/usr/bin/env django
# coding:utf-8

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^sync/', include('djproject.sync.urls')),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# EOF
