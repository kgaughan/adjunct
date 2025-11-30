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
test:
	@uv run --frozen pytest

# run the tests with coverage
coverage:
	@uv run --frozen pytest --cov=adjunct --cov-report=html

# run the typechecker
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
serve-docs:
	@# --livereload is needed because of https://github.com/squidfunk/mkdocs-material/issues/8478
	@uv run mkdocs serve --livereload
