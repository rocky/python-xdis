PHONY=check clean dist distclean test test-unit test-functional rmChangeLog clean_pyc nosetests

GIT2CL ?= git2cl
PYTHON ?= python

PYTHON_VERSION = $(shell $(PYTHON) -V | cut -d ' ' -f 2 | cut -d'.' -f1,2)

# Set COMPILE='--compile' to force compilation before check
COMPILE ?=

#: Run all tests
check: check-short
	$(PYTHON) test_pythonlib.py \
	 	  --bytecode-1.0 --bytecode-1.1 --bytecode-1.2 --bytecode-1.3 \
                  --bytecode-1.4 --bytecode-1.5 --bytecode-1.6 \
	          --bytecode-2.1 --bytecode-2.2 --bytecode-2.3 \
                  --bytecode-2.4 --bytecode-2.5 \
		  --bytecode-2.5dropbox \
                  --bytecode-2.6 --bytecode-2.7 \
		  --bytecode-3.0 --bytecode-3.1 \
                  --bytecode-3.2 --bytecode-3.3 \
                  --bytecode-3.4 --bytecode-3.5 \
	          --bytecode-3.6 --bytecode-3.7 --bytecode-3.8 \
	          --bytecode-3.9 --bytecode-3.10 \
	          --bytecode-2.7pypy --bytecode-3.2pypy \
                  --bytecode-3.5pypy --bytecode-3.6pypy --bytecode-3.7pypy $(COMPILE)
check-short:
	$(PYTHON) test_pyenvlib.py --verify --simple

check-bytecode-1.5:
	$(PYTHON) test_pythonlib.py --bytecode-1.5

check-bytecode-1:
	$(PYTHON) test_pythonlib.py \
	 	  --bytecode-1.0 --bytecode-1.1 --bytecode-1.2 --bytecode-1.3 \
                  --bytecode-1.4 --bytecode-1.5 --bytecode-1.6

check-bytecode-2:
	$(PYTHON) test_pythonlib.py \
	          --bytecode-2.1 --bytecode-2.2 --bytecode-2.3 \
                  --bytecode-2.4 --bytecode-2.5 \
		  --bytecode-2.5dropbox \
                  --bytecode-2.6 --bytecode-2.7

check-bytecode-3:
	$(PYTHON) test_pythonlib.py \
		  --bytecode-3.0 --bytecode-3.1 \
                  --bytecode-3.2 --bytecode-3.3 \
                  --bytecode-3.4 --bytecode-3.5 \
	          --bytecode-3.6 --bytecode-3.7 --bytecode-3.8

check-bytecode-3.8:
	$(PYTHON) test_pythonlib.py --bytecode-3.8

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

#: Clean temporary compile/decompile/verify directories in /tmp
clean-py-dis:
	rm -fr /tmp/py-dis-* || true
	rm -fr __pycache__ || true
