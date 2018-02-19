#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""

from __pkginfo__ import \
    author,           author_email,       \
    license,          long_description,   classifiers,               \
    modname,          py_modules,         setup_requires,            \
    scripts,          short_desc,         tests_require,             \
    VERSION,          web,                zip_safe

import itertools
from setuptools.command.test import test

# Python 2 setuptools test class is not an object
class TestsWithCoverage(test, object):

    description = "run unit tests with coverage"

    # Copypasta from setuptools 36.0.1 because older versions don't have it
    @staticmethod
    def install_dists(dist):
        ir_d = dist.fetch_build_eggs(dist.install_requires or [])
        tr_d = dist.fetch_build_eggs(dist.tests_require or [])
        return itertools.chain(ir_d, tr_d)


from setuptools import setup, find_packages
setup(
       author             = author,
       author_email       = author_email,
       classifiers        = classifiers,
       description        = short_desc,
       license            = license,
       long_description   = long_description,
       name               = modname,
       packages           = find_packages(),
       py_modules         = py_modules,
       setup_requires     = setup_requires,
       scripts            = scripts,
       tests_require      = tests_require,
       url                = web,
       version            = VERSION,
       zip_safe           = zip_safe)
