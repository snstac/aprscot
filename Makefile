# Makefile for Python APRS Cursor-on-Target Gateway.
#
# Source:: https://github.com/ampledata/aprscot
# Author:: Greg Albrecht W2GMD <oss@undef.net>
# Copyright:: Copyright 2021 Greg Albrecht
# License:: Apache License, Version 2.0
#


.DEFAULT_GOAL := all


all: develop

install_requirements:
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

install_requirements_test:
	pip install -r requirements_test.txt

develop:
	pip install -e .

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
		test-result.xml htmlcov fab.log .coverage */__pycache__/

# Publishing:

build: remember_test
	python3 -m build --sdist --wheel

twine_check: remember_test build
	twine check dist/*

upload: remember_test build
	twine upload dist/*

publish: build twine_check upload

# Tests:

pep8: remember_test
	# flake8 --max-complexity 12 --exit-zero *.py */*.py
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

flake8: pep8

lint: remember_test
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
	-r n *.py */*.py || exit 0

pylint: lint

pytest: remember_test
	pytest

test: lint pep8 pytest
