# Swiss Knife - Makefile for development and testing

.PHONY: help install install-dev test test-cov lint format security build clean demo

VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

help: ## Show this help message
	@echo "Swiss Knife - Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package in development mode
	$(PIP) install -e .

install-dev: ## Install with development dependencies
	$(PIP) install -e .[dev,all]

install-all: ## Install with all optional dependencies
	$(PIP) install -e .[all]

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ --cov=swiss_knife --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	$(PYTHON) -m pytest tests/ -q --disable-warnings

lint: ## Run linting checks
	$(PYTHON) -m ruff check swiss_knife/
	$(PYTHON) -m flake8 swiss_knife/

format: ## Format code
	$(PYTHON) -m ruff check swiss_knife/ --fix

security: ## Run security checks
	$(PYTHON) -m bandit -r swiss_knife/

typecheck: ## Run type checking (optional)
	$(PYTHON) -m mypy swiss_knife/ || true

quality: lint security typecheck ## Run all quality checks

build: ## Build package
	$(PYTHON) -m build

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

demo: ## Show CLI usage examples
	@echo "Swiss Knife - CLI Usage Examples"
	@echo "================================"
	@echo ""
	@echo "File Management:"
	@echo "  sk-duplicates ~/Documents --algorithm sha256"
	@echo "  sk-rename 'IMG_(\d+)' 'photo_\1' ~/Pictures --dry-run"
	@echo ""
	@echo "Text Processing:"
	@echo "  sk-csv data.csv --format json --pretty"
	@echo ""
	@echo "Security & Automation:"
	@echo "  sk-password --length 16 --symbols --exclude-ambiguous"
	@echo ""
	@echo "For more examples, see README_TESTING.md"

validate: ## Validate installation
	@echo "Validating Swiss Knife installation..."
	@$(PYTHON) -c "import swiss_knife; print(f'✓ Swiss Knife v{swiss_knife.__version__} installed')"
	@$(PYTHON) -c "from swiss_knife.file_management import find_duplicates; print('✓ File management module OK')"
	@$(PYTHON) -c "from swiss_knife.text_processing import convert_csv; print('✓ Text processing module OK')"
	@$(PYTHON) -c "from swiss_knife.automation import generate_password; print('✓ Automation module OK')"
	@echo "✓ All core modules validated"

check-cli: ## Check CLI entry points
	@echo "Checking CLI entry points..."
	@sk-duplicates --help > /dev/null && echo "✓ sk-duplicates" || echo "✗ sk-duplicates"
	@sk-csv --help > /dev/null && echo "✓ sk-csv" || echo "✗ sk-csv"  
	@sk-password --help > /dev/null && echo "✓ sk-password" || echo "✗ sk-password"

dev-setup: ## Set up development environment
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	$(MAKE) install-dev
	@echo "Development environment ready!"

ci: ## Run CI pipeline locally
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-cov
	$(MAKE) build

release-check: ## Check if ready for release
	@echo "Release readiness check..."
	$(MAKE) clean
	$(MAKE) quality
	$(MAKE) test-cov
	$(MAKE) build
	$(PYTHON) -m twine check dist/*
	@echo "✓ Release checks passed"
