PACKAGE_NAME = aws_vapor
TEST_ENVIRONMENTS = py36

default: test

test:
	tox -e ${TEST_ENVIRONMENTS}

clean:
	@rm -fr ${PACKAGE_NAME}.egg-info/* build/* dist/*

install: clean
	python3 setup.py install

package: clean
	python3 setup.py sdist bdist_wheel

pre-release:
	twine upload --repository pypitest dist/*

release:
	twine upload --repository pypi dist/*

.PHONY: test clean install package pre-release release
