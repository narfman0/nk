build: lint
	protoc proto/*.proto \
		--python_betterproto_out=../shared/nk_shared/ \
		--python_betterproto_out=../api/app/

lint:
	protolint lint -fix proto

watch: build
	python -m watcher