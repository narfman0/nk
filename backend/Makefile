run:
	uvicorn nk.main:app --reload --host 0.0.0.0 --port 7666

isort:
	isort --profile black nk

lint: isort
	pylint nk/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring