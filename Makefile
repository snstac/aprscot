# Makefile for Python APRS Cursor-on-Target Gateway.
#
# Source:: https://github.com/ampledata/aprscot
# Author:: Greg Albrecht W2GMD <oss@undef.net>
# Copyright:: Copyright 2020 Orion Labs, Inc.
# License:: Apache License, Version 2.0
#


.DEFAULT_GOAL := all


all: develop

install_requirements_test:
		pip install -r requirements_test.txt

develop:
	python setup.py develop

install:
	python setup.py install

uninstall:
	pip uninstall -y aprscot

reinstall: uninstall install

remember_test:
	@echo
	@echo "Hello from the Makefile..."
	@echo "Don't forget to run: 'make install_requirements_test'"
	@echo

clean:
	@rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log .coverage

publish:
	python setup.py register sdist upload

pep8: remember_test
	flake8 --max-complexity 12 --exit-zero *.py aprscot/*.py tests/*.py

flake8: pep8

lint: remember_test
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		-r n *.py aprscot/*.py tests/*.py || exit 0

pylint: lint

checkmetadata:
	python setup.py check -s --restructuredtext

test: lint pep8 pytest
