#!/usr/bin/env python
# coding=utf-8

"""
デプロイ用fabricスクリプト
"""

import os

import fabric.api
from fabric.api import cd, prefix, run
from fabric.decorators import task


'''
env.user = "fsync"
env.hosts = ['', ]
env.password = "J"
env.key_filename = [os.path.expanduser('~/.ssh/secret_key')]
'''

venv_basedir = "/var/gunicorn/venvs"
app_basedir = "/var/gunicorn/apps"


@task
def migration(app="fsync", djangoapps=["sync", ]):
    """
    データベースのマイグレーション
    """

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)
    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):
        # アプリケーション更新
        app_dirname = os.path.join(app_basedir, app)
        with cd(app_dirname):
            # マイグレーション
            run("python djproject/manage.py syncdb")
            for djangoapp in djangoapps:
                run("python djproject/manage.py migrate %s" % (djangoapp, ))


@task
def setup_supervisor(app="fsync"):
    """
    supervisorの設定ファイル更新
    """
    # 設定ファイルのコピー
    env_confs = {
        "dev.smiletechnology.jp": [
            "conf/fsync.ini",
            "/etc/supervisor.d/fsync.ini",
        ],
        "smiletechnology.jp": [],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]
    if not confirm("really setup %s?" % (hostname, )):
        fabric.api.abort("")

    for conf in confs:
        put(conf[0], conf[1])

    # supervisorのリロード
    pass


@task
def create_user(app="fsync"):
    """
    実行ユーザー作成
    """
    username = app
    groupname = app

    with fabric.api.settings(warn_only=True):
        # グループ作成
        if run("groupadd %s" % (groupname, )).failed:
            pass

        # ユーザー作成
        if run("id %s" % (username, )).failed:
            run("adduser -g %s %s" % (groupname, username))
            run("passwd %s" % (username, ))


@task
def create_table(app="fsync"):
    """
    データベース初期設定
    """

    # テーブル作成用sqlファイル
    confs = [
        "conf/create_table.sql",
    ]

    app_dirname = os.path.join(app_basedir, app)
    with cd(app_dirname):
        for conf in confs:
            run("mysql -u root -p < %s" % (conf, ))


@task
def deploy(app="fsync", repo="https://github.com/sporty/fruity-sync.git"):
    """
    デプロイ
    """

    #print(green("deploy "+app))

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)
    with fabric.api.settings(warn_only=True):
        if run("test -d "+venv_dirname).failed:
            run("virtualenv --distribute "+venv_dirname)

    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):

        # アプリケーション更新
        app_dirname = os.path.join(app_basedir, app)
        with fabric.api.settings(warn_only=True):
            if run("test -d %s" % (app_dirname, )).failed:
                # 取得
                run("git clone %s %s" % (repo, app_dirname))

        with cd(app_dirname):
            # 最新のファイルに更新
            run("git pull origin master")

            # モジュールの更新
            run("pip install -r requirements.txt")


@task
def start(app="fsync"):
    """
    サーバー起動または再起動
    """

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)

    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):

        app_dirname = os.path.join(app_basedir, app, "djproject")
        with cd(app_dirname):
            # サーバーの起動
            cmd = [
                "gunicorn",
                "--conf",
                "../conf/gunicorn.conf.py",
                "djproject.wsgi:application",
            ]
            run(" ".join(cmd))


@task
def reload(app="fsync"):
    """
    サーバー設定の再読み込み
    """

    pid_filename = "/var/run/gunicorn/%s.pid" % (app, )

    if run("test -f "+pid_filename):
        # サーバーの再読み込み
        run("kill -HUP `cat %s`" % (pid_filename, ))


# EOF
