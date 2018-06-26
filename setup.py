#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""

from __pkginfo__ import \
    author,           author_email,       \
    license,          long_description,   classifiers,               \
    modname,          py_modules,         \
    scripts,          short_desc,         tests_require,             \
    VERSION,          web,                zip_safe

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
       # setup_requires     = setup_requires,
       scripts            = scripts,
       tests_require      = tests_require,
       url                = web,
       version            = VERSION,
       zip_safe           = zip_safe)
