[private]
default:
	@just --list

# setup virtual environment
devel:
	@uv sync --frozen

# tidy everything with ruff
[group("Analysis/Fixing")]
tidy:
	@uv run --frozen ruff check --fix

# run the test suite
[group("Testing")]
test:
	@uv run --frozen pytest

# run only fast tests
[group("Testing")]
fast-test:
	@uv run --frozen pytest -m "not slow"

# run test suite showing the slowest of those not marked as slow
[group("Testing")]
test-show-slow:
	@uv run --frozen pytest -m "not slow" --durations 10

# run the tests with coverage
[group("Testing")]
coverage:
	@uv run --frozen pytest --cov=adjunct --cov-report=html

# run the typechecker
[group("Analysis/Fixing")]
typecheck:
	@uv run --frozen mypy src

# clean up any caches or temporary files and directories
clean:
	@rm -rf .mypy_cache .pytest_cache .ruff_cache .venv dist htmlcov .coverage tests/results.xml .coverage.*
	@find . -name \*.orig -delete

# install tools (you'll have to ensure you have uv already installed)
tools:
	@uv tool install ruff
	@uv tool install tox --with tox-uv

# run the mkdocs server
[group("Documentation")]
serve-docs:
	@# --livereload is needed because of https://github.com/squidfunk/mkdocs-material/issues/8478
	@uv run mkdocs serve --livereload
