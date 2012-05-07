#/usr/bin/env django
# coding:utf-8

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^$', 'djproject.views.home', name='home'),
    url(r'^sync/', include('djproject.sync.urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# EOF
