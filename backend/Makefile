run:
	uvicorn nk.main:app --reload --host 0.0.0.0 --port 7666

isort:
	isort --profile black nk

lint: isort
	pylint nk/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring

docker-build:
	cp -r ../data .
	find -type f -iname '*.png' -delete
	find -type f -iname '*.aseprite' -delete
	cp -r ../shared/nk_shared .
	docker build . -t narfman0/nk-backend-docker
	rm -rf data nk_shared

docker-deploy: docker-build
	docker push narfman0/nk-backend-docker

test:
	pytest --cov=nk --cov-report term-missing tests/