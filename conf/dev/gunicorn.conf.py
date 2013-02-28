#!/usr/bin/env python
# coding=utf-8

bind = "0.0.0.0:8000"
workers = 3
daemon = False
pidfile = '/var/run/gunicorn/fsync.pid'

user  = 'fsync'
group = 'fsync'
umask = 0002

settings = 'djproject.settings_dev'

loglevel = 'info'
logconfig = None
access_logfile = '/var/log/gunicorn/fsync_access.log'
error_logfile = '/var/log/gunicorn/fsync_error.log'

name = 'gunicorn_fsync'

# EOF
