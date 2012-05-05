#
# スタティックファイルのビルド
#

all: css 

css:
	lessc less/all.less > all.css
	lessc --compress less/all.less > all.min.css

clean:
	rm -rf all.css all.min.css

# EOF
