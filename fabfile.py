#!/usr/bin/env python
# coding=utf-8

"""
サーバー管理用fabricスクリプト
"""

import os
import datetime
import csv
import re
import fabric.api
from fabric.api import lcd, local, get, cd, prefix, run, abort
from fabric.contrib.console import confirm
from fabric.decorators import task
from fabric.colors import green, red


env.user = "fsync"
'''
env.hosts = ['', ]
env.password = "J"
env.key_filename = [os.path.expanduser('~/.ssh/secret_key')]
'''

@task
def host_name():
    """
    ホスト名を表示
    """
    local("uname -a")
    run("uname -a")


@task
def setup(local_dir="backup"):
    """
    セットアップ
    """

    pass

@task
def deploy(app="fsync", repo="https://github.com/sporty/fruity-sync.git"):
    """
    デプロイ
    """

    print(green("deploy "+app))

    venv_basedir = "/var/gunicorn/venvs"
    app_basedir = "/var/gunicorn/apps"

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)
    if run("test -d "+venv_dirname):
        run("virtualenv --distribute "+venv_dirname)

    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):

        # アプリケーション更新
        app_dirname = os.path.join(app_basedir, app)
        if run("test -d "+app_dirname):
            # 取得
            run("git clone %s %s" % (repo, app_dirname))

        with cd(app_dirname):
            # 最新のファイルに更新
            run("git pull origin master")

            # モジュールの更新
            run("pip install -r requirements.txt")

            # マイグレーション
            run("python djproject/manage.py syncdb")
            run("python djproject/manage.py migrate sync")


@task
def start(app="fsync"):
    """
    サーバー起動または再起動
    """
    venv_basedir = "/var/gunicorn/venvs"
    app_basedir = "/var/gunicorn/apps"

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)
    if run("test -d "+venv_dirname):
        error()

    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):

        app_dirname = os.path.join(app_basedir, app, "djproject")
        if run("test -d "+app_dirname):
            error()

        with cd(app_dirname):
            # サーバーの起動
            run("gunicorn --conf ../gunicorn.conf.py djproject.wsgi:application")

@task
def reload(app="fsync"):
    """
    サーバー起動または再起動
    """

    pid_filename = "/var/run/gunicorn/%s.pid" %(app, )

    if run("test -f "+pid_filename):
        # サーバーの再読み込み
        run("kill -HUP `cat %s`" % (pid_filename, ))


# EOF
