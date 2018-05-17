MAIN_PACKAGE = aws_vapor
TEST_ENVIRONMENT = py36

default: test

test: pipenv-lock
	tox -e ${TEST_ENVIRONMENT}

clean:
	@rm -fr ${MAIN_PACKAGE}.egg-info/* build/* dist/*

install:
	python3 setup.py install

package: clean pipenv-lock
	python3 setup.py sdist bdist_wheel

release:
	twine --help

pipenv-install:
	pipenv install --dev

pipenv-lock:
	pipenv lock -r >requirements.txt
	pipenv lock -r --dev >requirements-test.txt

.PHONY: test clean install package release pipenv-install pipenv-lock
