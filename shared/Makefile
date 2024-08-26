default: isort lint

isort:
	isort --profile black nk_shared
	isort --profile black tests

lint:
	pylint nk_shared/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring
