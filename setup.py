#!/usr/bin/env python

"""Setup script for the 'xdis' distribution."""

from __pkginfo__ import \
    author,           author_email,       \
    license,          long_description,   classifiers,               \
    modname,          py_modules,         scripts,                   \
    short_desc,       VERSION,            web,                       \
    zip_safe

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
       scripts            = scripts,
       test_suite         = 'nose.collector',
       url                = web,
       tests_require     = ['nose>=1.0'],
       version            = VERSION,
       zip_safe           = zip_safe)
