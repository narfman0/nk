default: isort lint

isort:
	isort --profile black nk_shared
	isort --profile black tests

lint:
	pylint nk_shared/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring --disable=C,R,W nk_shared/proto.py

mapgen:
	python -m nk_shared.map.mapgen