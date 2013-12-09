#!/usr/bin/env python
# coding=utf-8

"""
デプロイ用fabricスクリプト
"""

import os

import fabric.api
from fabric.api import cd, prefix, get, put, run, sudo
from fabric.decorators import task


'''
env.user = "fsync"
env.hosts = ['', ]
env.password = "J"
env.key_filename = [os.path.expanduser('~/.ssh/secret_key')]
'''

VENV_BASEDIR = "/var/gunicorn/venvs"
APP_BASEDIR = "/var/gunicorn/apps"

TMP_DIR = "/tmp"


def _put(src, dest):
    """
    一旦テンポラリディレクトリにputしてから
    sudoでコピーを行う
    """

    filename = os.path.basename(src)
    tmp_fullpathname = os.path.join(TMP_DIR, filename)

    # 一旦中間ファイルにコピー
    put(src, tmp_fullpathname)
    # root権限で中間ファイルから目的のファイルにコピー
    sudo("cp %s %s" % (tmp_fullpathname, dest))
    # 中間ファイル削除
    sudo("rm %s" % (tmp_fullpathname, ))

#
# https://github.com/sebastien/cuisine/blob/master/src/cuisine.py
#
def _file_exists(location):
    """Tests if there is a *remote* file at the given location."""
    return run('test -e "%s" && echo OK ; true' % (location)).endswith("OK")

def _file_is_file(location):
    return run("test -f '%s' && echo OK ; true" % (location)).endswith("OK")

def _file_is_dir(location):
    return run("test -d '%s' && echo OK ; true" % (location)).endswith("OK")

def _file_is_link(location):
    return run("test -L '%s' && echo OK ; true" % (location)).endswith("OK")


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
        "ec2-54-238-147-11.ap-northeast-1.compute.amazonaws.com": [
            ("conf/prod/logrotate/fsync",
                "/etc/logrotate.d/fsync"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(APP_BASEDIR, app)
    with cd(app_dirname):
        for conf in confs:
            _put(conf[0], conf[1])


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
        "ec2-54-238-147-11.ap-northeast-1.compute.amazonaws.com": [
            "conf/prod/cron.txt",
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    cronfile = confs[0]

    app_dirname = os.path.join(APP_BASEDIR, app)
    with cd(app_dirname):
        if disable==True:
            sudo("crontab -u fsync -r")
        else:
            sudo("crontab -u fsync %s" % (cronfile, ))


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
        "ec2-54-238-147-11.ap-northeast-1.compute.amazonaws.com": [
            ("conf/prod/supervisor/fsync.ini",
                "/etc/supervisord.d/fsync.ini"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(APP_BASEDIR, app)
    with cd(app_dirname):
        for conf in confs:
            _put(conf[0], conf[1])

    # supervisordの再起動
    sudo("/etc/init.d/supervisord restart")


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
        "ec2-54-238-147-11.ap-northeast-1.compute.amazonaws.com": [
            ("conf/prod/nginx/fsync.conf",
                "/etc/nginx/conf.d/fsync.conf"),
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    app_dirname = os.path.join(APP_BASEDIR, app)
    with cd(app_dirname):
        for conf in confs:
            _put(conf[0], conf[1])

    # nginxの再起動
    sudo("/etc/init.d/nginx restart")


@task
def setup_database(app="fsync", host="mysqlinstance.ckoq5hf60pxi.ap-northeast-1.rds.amazonaws.com", user="root"):
    """
    データベース初期設定
    """

    # テーブル作成用sqlファイル
    confs = [
        "conf/common/create_table.sql",
    ]

    app_dirname = os.path.join(APP_BASEDIR, app)
    with fabric.api.settings(warn_only=True):
        with cd(app_dirname):
            for conf in confs:
                sudo("mysql -h %s -u %s -p < %s" % (host, user, conf))


@task
def setup_user(app="fsync"):
    """
    実行ユーザー作成
    """
    username = app
    groupname = app

    with fabric.api.settings(warn_only=True):
        # グループ作成
        if sudo("groupadd %s" % (groupname, )).failed:
            pass

        # ユーザー作成
        if sudo("id %s" % (username, )).failed:
            sudo("adduser -g %s %s" % (groupname, username))
            sudo("passwd %s" % (username, ))


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
        "ec2-54-238-147-11.ap-northeast-1.compute.amazonaws.com": [
            "djproject.settings_prod",
        ],
    }

    hostname = fabric.api.env.host
    confs = env_confs[hostname]

    settings_file = confs[0]

    # venvの切り替え
    venv_dirname = os.path.join(VENV_BASEDIR, app)
    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):
        # アプリケーション更新
        app_dirname = os.path.join(APP_BASEDIR, app)
        with cd(app_dirname):
            # マイグレーション
            sudo("python djproject/manage.py syncdb --settings=%s" % (settings_file, ))
            for djangoapp in djangoapps:
                sudo("python djproject/manage.py migrate %s --settings=%s" % (djangoapp, settings_file))


@task
def deploy(app="fsync", repo="git@github.com:sporty/FruitySync.git"):
    """
    デプロイ
    """

    #print(green("deploy "+app))

    # venvの切り替え
    venv_dirname = os.path.join(VENV_BASEDIR, app)
    with fabric.api.settings(warn_only=True):
        if not _file_is_dir(venv_dirname):
            sudo("virtualenv --distribute --python /usr/bin/python2.7 %s" % (venv_dirname, ))

    # venv環境セットアップ
    with prefix("source "+os.path.join(venv_dirname, "bin/activate")):

        # アプリケーション更新
        app_dirname = os.path.join(APP_BASEDIR, app)
        with fabric.api.settings(warn_only=True):
            if not _file_is_dir(app_dirname):
                # 取得
                if sudo("git clone %s %s" % (repo, app_dirname)).failed:
                    fabric.api.abort("can't clone git repository. (%s)" % (repo, ))

        with cd(app_dirname):
            # 最新のファイルに更新
            sudo("git pull origin master")

            # モジュールの更新
            sudo("pip install -r requirements.txt")


@task
def bootstrap(app="fsync"):
    """
    """
    deploy()
    setup_all()
    migration()


@task
def reload(app="fsync"):
    """
    サーバープロセスの再起動
    """

    # supervisorのリロード
    sudo("/etc/init.d/supervisord restart")


# EOF
