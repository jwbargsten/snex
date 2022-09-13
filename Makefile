.PHONY: all clean test

date=$(shell date +%F)

all:

test:
	poetry run pytest -vvs

build:
	. .venv/bin/activate && poetry build
run:
	poetry run snex --config_file ./snex.repo.conf

lint: ## run mypy and flake8 to check the code
	poetry run flake8 src tests

fmt: ## run black to format the code
	poetry run black src tests
