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
def setup_logrotate(app="fsync"):
    """
    logrotateの設定
    """

    # 設定ファイルのコピー
    env_confs = {
        "dev.smiletechnology.jp": [
            ("conf/dev/logrotate/fsync",
                "/etc/logrotate.d/fsync"),
        ],
        "smiletechnology.jp": [
            ("conf/prod/logrotate/fsync",
                "/etc/logrotate.d/fsync"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(app_basedir, app)
    with cd(app_dirname):
        for conf in confs:
            run("cp %s %s" % (conf[0], conf[1]))


@task
def setup_cron(app="fsync", disable=False):
    """
    crontabの設定
    """

    env_confs = {
        "dev.smiletechnology.jp": [
            "conf/dev/cron.txt",
        ],
        "smiletechnology.jp": [
            "conf/prod/cron.txt",
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    cronfile = confs[0]

    app_dirname = os.path.join(app_basedir, app)
    with cd(app_dirname):
        if disable==True:
            run("crontab -u fsync -r")
        else:
            run("crontab -u fsync %s" % (cronfile, ))


@task
def setup_supervisor(app="fsync"):
    """
    supervisorの設定
    """

    # 設定ファイルのコピー
    env_confs = {
        "dev.smiletechnology.jp": [
            ("conf/dev/supervisor/fsync.ini",
                "/etc/supervisord.d/fsync.ini"),
        ],
        "smiletechnology.jp": [
            ("conf/prod/supervisor/fsync.ini",
                "/etc/supervisord.d/fsync.ini"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(app_basedir, app)
    with cd(app_dirname):
        for conf in confs:
            run("cp %s %s" % (conf[0], conf[1]))

    # supervisordの再起動
    run("/etc/init.d/supervisord restart")


@task
def setup_nginx(app="fsync"):
    """
    nginxの設定
    """

    # 設定ファイルのコピー
    env_confs = {
        "dev.smiletechnology.jp": [
            ("conf/dev/nginx/fsync.conf",
                "/etc/nginx/conf.d/fsync.conf"),
        ],
        "smiletechnology.jp": [
            ("conf/prod/nginx/fsync.conf",
                "/etc/nginx/conf.d/fsync.conf"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(app_basedir, app)
    with cd(app_dirname):
        for conf in confs:
            run("cp %s %s" % (conf[0], conf[1]))


    # nginxの再起動
    run("/etc/init.d/nginx restart")


@task
def setup_database(app="fsync"):
    """
    データベース初期設定
    """

    # テーブル作成用sqlファイル
    confs = [
        "conf/common/create_table.sql",
    ]

    app_dirname = os.path.join(app_basedir, app)
    with fabric.api.settings(warn_only=True):
        with cd(app_dirname):
            for conf in confs:
                run("mysql -u root -p < %s" % (conf, ))


@task
def setup_user(app="fsync"):
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
def setup_all(app="fsync"):
    """
    全セットアップ
    """

    setup_user(app)
    setup_database(app)
    setup_nginx(app)
    setup_supervisor(app)
    setup_cron(app)
    setup_logrotate(app)


@task
def migration(app="fsync", djangoapps=["sync", ]):
    """
    データベースのマイグレーション
    """
    env_confs = {
        "dev.smiletechnology.jp": [
            "djproject.settings_dev",
        ],
        "smiletechnology.jp": [
            "djproject.settings_prod",
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    settings_file = confs[0]

    # venvの切り替え
    venv_dirname = os.path.join(venv_basedir, app)
    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):
        # アプリケーション更新
        app_dirname = os.path.join(app_basedir, app)
        with cd(app_dirname):
            # マイグレーション
            run("python djproject/manage.py syncdb --settings=%s" % (settings_file, ))
            for djangoapp in djangoapps:
                run("python djproject/manage.py migrate %s --settings=%s" % (djangoapp, settings_file))


@task
def deploy(app="fsync", repo="git@github.com:sporty/FruitySync.git"):
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
                if run("git clone %s %s" % (repo, app_dirname)).failed:
                    fabric.api.abort("can't clone git repository. (%s)" % (repo, ))

        with cd(app_dirname):
            # 最新のファイルに更新
            run("git pull origin master")

            # モジュールの更新
            run("pip install -r requirements.txt")


@task
def bootstrap(app="fsync"):
    """
    """
    deploy()
    migration()
    setup_all()


@task
def reload(app="fsync"):
    """
    サーバープロセスの再起動
    """

    # supervisorのリロード
    #run("supervisorctl restart fsync")
    run("/etc/init.d/supervisord restart")
    #run("/etc/init.d/nginx restart")


# EOF
