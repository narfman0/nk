default: app

clean: clean-build clean-pyc clean-installer

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info
	rm -f .coverage
	rm -f *.log

clean-installer:
	rm -fr output/
	rm -fr app.spec
	rm -f nk.spec
	rm -f nk.zip

clean-pyc: ## remove Python file artifacts
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +

init:
	pip install -r requirements.txt

init-dev:
	pip install -r requirements_test.txt

isort:
	isort --profile black nk
	isort --profile black tests

lint: isort
	pylint nk/ -d missing-function-docstring,missing-class-docstring,missing-module-docstring,too-few-public-methods

pyinstaller: clean
	pyinstaller --noconfirm --onefile --console \
		-n nk --uac-admin \
		app.py
	cp -r ../data/ dist/
	cp ../data/installer/*.dll dist/
	cp README.* dist/
	7z a nk.zip dist/*
	7z rn nk.zip dist nk

test:
	pytest --cov=nk --cov-report term-missing -W ignore::DeprecationWarning tests/

app:
	python -m app

release: test clean pyinstaller

headless:
	python -m nk.headless
