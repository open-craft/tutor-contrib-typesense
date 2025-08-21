.DEFAULT_GOAL := help
.PHONY: test install format lint help

test: lint  ## Run all tests

install: ## Install python dependencies (it's recommended to activate a virtualenv first)
	pip install -e .[dev]
	@which shellcheck > /dev/null || (echo "'shellcheck' is not available. Please manually install shellcheck to run tests." && exit 1)

lint: ## Run code linting tests
	black --check --diff tutor_typesense
	pylint --errors-only --enable=unused-import,unused-argument --ignore=templates --ignore=docs/_ext tutor_typesense
	mypy --exclude=templates --ignore-missing-imports --implicit-reexport --strict tutor_typesense
	shellcheck tutor_typesense/templates/typesense/tasks/typesense/init.sh

format: ## Format code automatically
	isort tutor_typesense
	black tutor_typesense

ESCAPE = 
help: ## Print this help
	@grep -E '^([a-zA-Z_-]+:.*?## .*|######* .+)$$' Makefile \
		| sed 's/######* \(.*\)/@               $(ESCAPE)[1;31m\1$(ESCAPE)[0m/g' | tr '@' '\n' \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[33m%-30s\033[0m %s\n", $$1, $$2}'
