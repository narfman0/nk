run:
	python -m app.main

isort:
	isort --profile black app
	isort --profile black tests

lint: isort
	pylint app/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring

test:
	pytest --cov=app --cov-report term-missing -W ignore::DeprecationWarning tests/
