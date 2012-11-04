
all:

deploy:
	git push heroku master

commit:
	git push origin master

package:
	pip freeze > requirements


