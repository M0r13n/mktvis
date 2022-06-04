flake:
	flake8 ./mktvis

ansible_lint:
	yamllint ./setup
	ansible-lint ./setup

.PHONY: build
build:
	rm -rf dist/ && rm -rf build/ && python setup.py sdist bdist_wheel

check-build:
	twine check dist/*

type-check:
	mypy --install-types ./mktvis

clean:
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm coverage.xml
	rm .coverage

test: flake type-check ansible_lint

install:
	pip install wheel
	pip install -U .[dev]
	pip install -U yamllint ansible-lint ansible

run:
	python main.py