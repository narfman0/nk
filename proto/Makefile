SRC_DIR := proto/
BUILD_DIR := ../shared/nk_shared/

build: build_dir lint
	protoc --python_betterproto_out=$(BUILD_DIR) $(SRC_DIR)*.proto

build_dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

lint:
	protolint lint -fix proto

watch: build
	python -m watcher