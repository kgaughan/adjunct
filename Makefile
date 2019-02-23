tests:
	python3 -m unittest

coverage:
	coverage run --source adjunct -m unittest
	coverage report

report:
	coverage html

.PHONY: tests coverage report
