.PHONY: all clean init setup install test lint format docs

# Variables
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
SRC := src
TESTS := tests

# Default target
all: help

# Help message
help:
	@echo "TF-Canary CAN-Bus Simulator - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make init              Initialize development environment"
	@echo "  make setup             Set up Pixi environment"
	@echo "  make install           Install the package in development mode"
	@echo "  make test              Run tests"
	@echo "  make lint              Run linter (ruff)"
	@echo "  make format            Format code (black + isort)"
	@echo "  make clean             Clean up build artifacts and caches"
	@echo "  make docs              Generate documentation"

# Initialize development environment
init:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e ".[dev]"

# Set up Pixi environment
setup:
	$(BIN)/python -m src.env.pixi_environment

# Install the package in development mode
install:
	$(BIN)/pip install -e .

# Run tests
test:
	$(BIN)/pytest $(TESTS)

# Run with coverage report
test-cov:
	$(BIN)/pytest --cov=$(SRC) --cov-report=term --cov-report=html $(TESTS)

# Run linter
lint:
	$(BIN)/ruff check $(SRC) $(TESTS)

# Format code
format:
	$(BIN)/isort $(SRC) $(TESTS)
	$(BIN)/black $(SRC) $(TESTS)

# Clean up build artifacts and caches
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Generate documentation
docs:
	@echo "Documentation generation not yet implemented"
