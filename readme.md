facebook->twitter同期アプリケーション
=====================================

環境設定のメモ
--------------

* virtualenv

```
virtualenv --distriute venv
pip install Django South django-debug-toolbar gunicorn psycopg2 tweepy facebook-sdk
pip freeze > requirements.txt
```

* git初期化

```
git init
echo "venv" >> .gitignore
git add Procfile djproject readme.md requirements.txt .gitignore 
git commit
 
git remote add origin git@github.com:sporty/fruity-sync.git
git push origin master
```

* heroku初期化

```
heroku create --stack cedar
heroku addons:add shared-database
heroku addons:add scheduler:standard
```

Deploy手順
----------

* メンテナンスモード

* Push

```
git push heroku master
```

* マイグレーション

初回

```
heroku run python djproject/manager syncdb
```

更新

```
heroku run python djproject/manager migrate
```


