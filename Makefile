build:
	find . -name \*.orig -delete
	poetry build --format wheel

tests:
	poetry run python3 -m unittest

coverage:
	poetry run coverage run --source adjunct -m unittest
	poetry run coverage report

report: coverage
	poetry run coverage html

tidy:
	poetry run black adjunct tests
	poetry run isort adjunct tests

lint: 
	poetry run black --check adjunct tests
	poetry run isort --check adjunct tests
	@# This ignore if required by something black does with ':'
	poetry run flake8 --max-line-length=105 --ignore=E203 --per-file-ignores="adjunct/oembed.py:N802 adjunct/opml.py:N802" adjunct
	poetry run pylint adjunct

.PHONY: build tests coverage report tidy lint
