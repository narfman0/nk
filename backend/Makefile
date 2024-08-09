run:
	uvicorn nk.main:app --reload --host 0.0.0.0 --port 7666

isort:
	isort --profile black nk
	isort --profile black tests

lint: isort
	pylint nk/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring

test:
	pytest --cov=nk --cov-report term-missing -W ignore::DeprecationWarning tests/
