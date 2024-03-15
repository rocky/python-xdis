#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""
from setuptools import find_packages, setup

from __pkginfo__ import (
    author,
    author_email,
    classifiers,
    entry_points,
    install_requires,
    license,
    long_description,
    modname,
    python_requires,
    short_desc,
    tests_require,
    web,
    zip_safe,
)
from xdis.version import __version__

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
    python_requires=python_requires,
    # setup_requires     = setup_requires,
    tests_require=tests_require,
    url=web,
    version=__version__,
    zip_safe=zip_safe,
)
