develop:
	poetry update --no-ansi -n

build:
	find . -name \*.orig -delete
	poetry build --format wheel

tests: develop
	poetry run pytest

tidy: develop
	poetry run black adjunct tests
	poetry run isort adjunct tests

lint: develop
	poetry run black --check adjunct tests
	poetry run isort --check adjunct tests
	@# This ignore if required by something black does with ':'
	poetry run flake8 --max-line-length=105 --ignore=E203 --per-file-ignores="adjunct/oembed.py:N802 adjunct/opml.py:N802" adjunct
	poetry run pylint adjunct

.PHONY: build develop tests tidy lint
