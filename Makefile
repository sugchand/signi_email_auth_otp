.PHONY: help venv install dev test coverage lint format clean

PIP := .venv/bin/pip
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
BLACK := .venv/bin/black
FLAKE8 := .venv/bin/flake8
MYPY := .venv/bin/mypy


help:
	@echo "Usage:"
	@echo "  make venv        Create virtual environment"
	@echo "  make activate    Print activation command"
	@echo "  make install     Install prod + dev dependencies from pyproject.toml"
	@echo "  make test        Run all tests"
	@echo "  make coverage    Run tests with coverage report"
	@echo "  make lint        Run flake8"
	@echo "  make format      Run black"
	@echo "  make typecheck   Run mypy static type checker"
	@echo "  make clean       Remove cache and venv"

venv:
	@test -d .venv || python3 -m venv .venv

activate:
	@echo "Run: source .venv/bin/activate"

install: venv
	$(PIP) install pip --upgrade
	$(PIP) install .[dev]

test:
	PYTHONPATH=./src $(PYTEST) tests/

coverage:
	PYTHONPATH=./src $(PYTEST) --cov=signi_email_otp --cov-report=term-missing tests/

lint:
	$(FLAKE8) ./src/signi_email_otp tests

format:
	$(BLACK) ./src/signi_email_otp tests

typecheck:
	$(MYPY) ./src/

clean:
	rm -rf .venv __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name '__pycache__' -exec rm -r {} +
