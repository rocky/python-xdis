#!/usr/bin/env python
"""Setup script for the 'xdis' distribution.

  Check that the Python version running this is compatible with this installation medium.
  Note: that we use 2.x compatible Python code here.
"""
import sys
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
    py_modules,
    short_desc,
    tests_require,
    web,
    zip_safe,
)
from xdis.version import __version__

major = sys.version_info[0]
minor = sys.version_info[1]

if major != 3 or not 0 <= minor < 3:
    sys.stderr.write("This installation medium is only for Python 3.0 to 3.2. You are running Python %s.%s.\n" % (major, minor))
elif major == 3 and minor >= 11:
    sys.stderr.write("Please install using xdis-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)
elif major == 6 and minor < 11:
    sys.stderr.write("Please install using xdis_36-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)
if major == 3 and 3 <= minor < 6:
    sys.stderr.write("Please install using xdis_33-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)
elif major == 2:
    sys.stderr.write("Please install using xdis_24-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)


setup(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    entry_points=entry_points,
    install_requires=install_requires,
    license=license,
    long_description=long_description,
    name=modname,
    packages=find_packages(),
    py_modules=py_modules,
    # setup_requires     = setup_requires,
    tests_require=tests_require,
    url=web,
    version=__version__,
    zip_safe=zip_safe,
)
