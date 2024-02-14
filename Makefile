.PHONY: all clean test
.DEFAULT_GOAL := help

VENV?=.venv
PIP=$(VENV)/bin/pip
PY=$(VENV)/bin/python


test: ## run tests
	. $(VENV)/bin/activate && pytest tests/

tags: ## build a ctags file for jwb's crappy editor
	ctags --languages=python -f tags -R src tests

run:
	snex --config_file ./snex.repo.conf

lint: ## lint the source code
	. $(VENV)/bin/activate && ruff check src/ tests/
	. $(VENV)/bin/activate && ruff format --check src/ tests/

fmt: ## format the source code with ruff
	. $(VENV)/bin/activate && ruff format src/ tests/
	. $(VENV)/bin/activate && ruff check --fix src/ tests/

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info

build: clean $(VENV)/init ## build the pkg
	$(PY) -m build

install-editable: $(VENV)/init
	. $(VENV)/bin/activate && $(PIP) install -e '.[dev]'

install: $(VENV)/init
	. $(VENV)/bin/activate && $(PIP) install '.[dev]'

dist: build
	. $(VENV)/bin/activate && check-manifest
	. $(VENV)/bin/activate && check-wheel-contents
	. $(VENV)/bin/activate && pyroma -n 6 .
	. $(VENV)/bin/activate && $(PY) -m twine check dist/*
	@echo ". $(VENV)/bin/activate && $(PY) -m twine upload dist/*"

$(VENV)/init: pyproject.toml Makefile ## init the virtual environment
	  python -m venv $(VENV)
	  $(PIP) install --upgrade build twine
	  touch $@

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9._-]+:.*?## / {printf "\033[1m\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
