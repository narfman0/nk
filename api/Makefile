run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 7666

isort:
	isort --profile black app
	isort --profile black tests

lint: isort
	pylint app/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring --ignore proto.py

test:
	pytest --cov=app --cov-report term-missing -W ignore::DeprecationWarning tests/
