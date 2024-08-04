run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

isort:
	isort --profile black app/

lint: isort
	pylint app/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring

docker-build:
	docker build . -t narfman0/nk-auth-docker

docker-deploy: docker-build
	docker push narfman0/nk-auth-docker