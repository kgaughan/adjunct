COVERAGE:=python3 -m coverage

tests:
	python3 -m unittest

coverage:
	$(COVERAGE) run --source adjunct -m unittest
	$(COVERAGE) report

report: coverage
	$(COVERAGE) html

.PHONY: tests coverage report
