#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""
from xdis.version import __version__

from __pkginfo__ import (
    author,
    author_email,
    entry_points,
    install_requires,
    license,
    long_description,
    classifiers,
    modname,
    py_modules,
    py_modules,
    python_requires,
    short_desc,
    tests_require,
    web,
    zip_safe,
)

from setuptools import setup, find_packages

setup(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    entry_points=entry_points,
    install_requires=install_requires,
    license=license,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    name=modname,
    packages=find_packages(),
    py_modules=py_modules,
    python_requires=python_requires,
    # setup_requires     = setup_requires,
    tests_require=tests_require,
    url=web,
    version=__version__,
    zip_safe=zip_safe,
)
