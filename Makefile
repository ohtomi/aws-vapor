MAIN_PACKAGE = aws_vapor
TEST_ENVIRONMENT = py36

default: test

test:
	tox -e ${TEST_ENVIRONMENT}

clean:
	@rm -fr ${MAIN_PACKAGE}.egg-info/* build/* dist/*

install: clean
	python3 setup.py install

package: clean
	python3 setup.py sdist bdist_wheel

release:
	twine --help

pipenv-install:
	pipenv install --dev --skip-lock

.PHONY: test clean install package release pipenv-install
