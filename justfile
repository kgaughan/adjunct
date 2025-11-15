[private]
default:
	@just --list

# setup virtual environment
devel:
	@uv sync --frozen

# tidy everything with ruff
tidy:
	@uv run --frozen ruff check --fix

# run the test suite
tests:
	@uv run --frozen pytest

clean:
	@rm -rf .venv .pytest_cache htmlcov dist .coverage
