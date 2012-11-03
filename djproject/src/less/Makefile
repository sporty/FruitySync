#
# スタティックファイルのビルド
#
TARGET_DIR=../../static/local/css

all: css 

css:
	lessc sync/all.less > $(TARGET_DIR)/main.css
	lessc --compress sync/all.less > $(TARGET_DIR)/main.min.css

clean:
	rm -rf main.css main.min.css

# EOF
