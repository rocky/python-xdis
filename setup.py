#!/usr/bin/env python
"""Setup script for the 'xdis' distribution."""
import sys
from xdis.version import __version__
from setuptools import setup, find_packages

SYS_VERSION = sys.version_info[0:2]
if not ((2, 4) <= SYS_VERSION <= (2, 7)):
    mess = "Python Release 2.4 .. 2.7 are supported in this code branch."
    if SYS_VERSION >= (3, 6):
        mess += (
            "\nFor your Python, version %s, use the master branch."
            % sys.version[0:3]
        )
    elif (3, 3) <= SYS_VERSION < (3, 6):
        mess += (
            "\nFor your Python, version %s, use the python-3.3-3.5 branch."
            % sys.version[0:3]
        )
    elif (3, 0) <= SYS_VERSION < (3, 3):
        mess += (
            "\nFor your Python, version %s, use the python-3.0-3.2 branch."
        )
    else:
        mess += (
            "\nThis package is not supported for Python version %s." % sys.version[0:3]
        )

    print(mess)
    raise Exception(mess)

from __pkginfo__ import (
    author,
    author_email,
    classifiers,
    entry_points,
    install_requires,
    license,
    long_description,
    modname,
    py_modules,
    short_desc,
    tests_require,
    web,
    zip_safe,
)

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
    # setup_requires     = setup_requires,
    tests_require=tests_require,
    url=web,
    version=__version__,
    zip_safe=zip_safe,
)
