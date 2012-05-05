#/usr/bin/env django
# coding:utf-8

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', 'djproject.views.home', name='home'),
    url(r'^auth/', include('djproject.auth.urls')),
    url(r'^tenko/', include('djproject.tenko.urls')),
    url(r'^fat/', include('djproject.fat.urls')),
    url(r'^twitter/', include('djproject.twitter.urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# EOF
