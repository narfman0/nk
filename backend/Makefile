run:
	uvicorn nk.main:app --reload --host 0.0.0.0 --port 7666

isort:
	isort --profile black nk

lint: isort
	pylint nk/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring

deploy:
	cp -r ../data .
	find -type f -iname '*.png' -delete
	cp -r ../shared/nk_shared .
	docker build . -t narfman0/nk-backend-docker
	docker push narfman0/nk-backend-docker
	rm -rf data nk_shared