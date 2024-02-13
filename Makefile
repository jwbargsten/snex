.PHONY: all clean test
.DEFAULT_GOAL := help

test: ## run tests
	pytest tests/

tags: ## build a ctags file for jwb's crappy editor
	ctags --languages=python -f tags -R src tests

run:
	snex --config_file ./snex.repo.conf

lint: ## lint the source code
	ruff check src/ tests/
	ruff format --check src/ tests/

fmt: ## format the source code with ruff
	ruff format src/ tests/
	ruff check --fix src/ tests/

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9._-]+:.*?## / {printf "\033[1m\033[36m%-38s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
