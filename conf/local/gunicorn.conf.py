#!/usr/bin/env python
# coding=utf-8

bind = "0.0.0.0:8000"
workers = 1
daemon = False

django_settings = 'djproject.settings_dev'

loglevel = 'info'
logconfig = None

name = 'gunicorn_fsync'

# EOF
