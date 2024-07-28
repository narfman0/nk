SRC_DIR := nk/
BUILD_DIR := build/

build: build_dir
	protoc --python_betterproto_out=$(BUILD_DIR) $(SRC_DIR)**/*.proto

build_dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

deploy: build
	cp -r $(BUILD_DIR)nk/* ../shared/nk_shared

watch:
	python -m watcher