.PHONY: all clean test

date=$(shell date +%F)

all:

test:
	poetry run pytest -vvs

build:
	. .venv/bin/activate && poetry build
run:
	poetry run snex --config_file ./snex.repo.conf
