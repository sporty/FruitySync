#/usr/bin/env django
# coding:utf-8

from django.conf import settings
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

if not settings.DEBUG:
    # DEBUGモードでない場合は自前でサービング
    urlpatterns += patterns('',
            url(r'^'+settings.STATIC_URL[1:]+'(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.STATIC_ROOT,
            }),
    )

# EOF
