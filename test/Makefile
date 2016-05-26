PHONY=check clean dist distclean test test-unit test-functional rmChangeLog clean_pyc nosetests

GIT2CL ?= git2cl
PYTHON ?= python

PYTHON_VERSION = $(shell $(PYTHON) -V | cut -d ' ' -f 2 | cut -d'.' -f1,2)

# Set COMPILE='--compile' to force compilation before check
COMPILE ?=

#: Run all tests
check check-short:
	$(PYTHON) test_pyenvlib.py --verify --simple

#: Test of all pyenv Python library files
check-full check-pyenv:
	$(PYTHON) test_pyenvlib.py --verify

#: Run all tests
check-ci:
	$(PYTHON) test_pyenvlib.py --verify --simple --compile

clean: clean-py-dis clean-dis clean-unverified

clean-dis:
	find . -name '*_dis' -exec rm -v '{}' ';'

clean-unverified:
	find . -name '*_unverified' -exec rm -v '{}' ';'

#: Clean temporary compile/decompile/verify direcotries in /tmp
clean-py-dis:
	rm -fr /tmp/py-dis-* || true
