build:
	hatch build

tidy:
	hatch run style:fmt

lint:
	hatch run style:check

test:
	hatch run test:unit

.PHONY: build test tidy lint
