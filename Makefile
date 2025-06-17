.PHONY: help install lint format check test coverage clean pre-commit

help:
	@echo "Available targets:"
	@echo "  install     - Install all dependencies"
	@echo "  lint        - Run ruff linter"
	@echo "  format      - Run ruff formatter"
	@echo "  check       - Run all checks (lint, format, type, security)"
	@echo "  test        - Run tests"
	@echo "  coverage    - Run tests with coverage"
	@echo "  clean       - Clean up temporary files"
	@echo "  pre-commit  - Run pre-commit hooks"

install:
	uv pip install -r requirements.txt

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

type-check:
	uv run mypy . || true

security:
	uv run bandit -r . -f json -o bandit-report.json || true

check: lint format-check type-check security pre-commit
	@echo "All checks completed"

test:
	uv run pytest tests/ -v

coverage:
	uv run pytest tests/ --cov=domains --cov=ui --cov-report=html --cov-report=term

pre-commit:
	uv run pre-commit run --all-files

pre-commit-install:
	uv run pre-commit install

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf bandit-report.json
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
