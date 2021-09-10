# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8

#EXTRA_DIST=ipython/ipy_trepan.py trepan
PHONY=all check clean dist-older dist-newer unittest check-long dist distclean lint flake8 test rmChangeLog clean_pyc

TEST_TYPES=check-long check-short check-2.7 check-3.4

#: Default target - same as "check"
all: check

#: Run all tests, exluding those that need pyenv
check: unittest
	@PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2`; \
	$(MAKE) -C test check

check-ci: unittest
	@PYTHON_VERSION=`$(PYTHON) -V 2>&1 | cut -d ' ' -f 2 | cut -d'.' -f1,2`; \
	$(MAKE) -C test check-ci

#: All tests including pyenv library tests
check-full: check
	$(MAKE) -C test check-pyenv

#: Run all quick tests
check-short: unittest pytest
	$(MAKE) -C test check-short

#: Run unittests tests
unittest:
	py.test pytest

#: Clean up temporary files and .pyc files
clean: clean_pyc
	$(PYTHON) ./setup.py $@
	find . -name __pycache__ -exec rm -fr {} \; || true
	(cd test && $(MAKE) clean)
	(cd test_unit && $(MAKE) clean)

#: Create source (tarball) and wheel distribution
dist: clean
	$(PYTHON) ./setup.py sdist bdist_egg

#: Create older distributions
dist-older:
	bash ./admin-tools/make-dist-older.sh

#: Create newer distributions
dist-newer:
	bash ./admin-tools/make-dist-newer.sh

#: Remove .pyc files
clean_pyc:
	( cd xdis && $(RM) -f *.pyc */*.pyc )

#: Create source tarball
sdist:
	$(PYTHON) ./setup.py sdist

#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint: flake8

#: Check StructuredText long description formatting
check-rst:
	$(PYTHON) setup.py --long-description | rst2html.py > xdis-trepan.html

#: Run tests across the newer Python versions supported
check-newer:
	$(BASH) admin-tools/check-newer-versions.sh

#: Run tests across the older Python versions supported
check-older:
	$(BASH) admin-tools/check-older-versions.sh

#: Lint program
flake8:
	$(LINT) xdis

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg


#: Create binary wheel distribution
bdist_wheel:
	$(PYTHON) ./setup.py bdist_wheel

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.pyc

#: Remove ALL derived files
distclean: clean
	-rm -fvr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

#: Install package locally
verbose-install:
	$(PYTHON) ./setup.py install

#: Install package locally without the verbiage
install:
	$(PYTHON) ./setup.py install >/dev/null

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
