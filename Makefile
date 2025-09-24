# Default Python version
PYTHON := python3
VENV := venv

.PHONY: help setup install test clean lint format

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create virtual environment
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip

install: ## Install all dependencies
	./$(VENV)/bin/pip install -r convert/requirements.txt
	./$(VENV)/bin/pip install -r automation/requirements.txt || true

test: ## Run all tests
	find . -name "*.py" -exec $(PYTHON) -m py_compile {} \;

lint: ## Lint all Python files
	./$(VENV)/bin/flake8 --max-line-length=100 .

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf $(VENV)

package: ## Create distribution package
	mkdir -p dist/
	tar -czf dist/sacred-scripts.tar.gz --exclude='.git' --exclude='venv' .
