#!/usr/bin/env python
"""Setup script for the 'xdis' distribution.

  Check that the Python version running this is compatible with this installation medium.
  Note: that we use 2.x compatible Python code here.
"""
import sys
from xdis.version import __version__
from setuptools import setup, find_packages

SYS_VERSION = sys.version_info[0:2]
if not ((3, 0) <= SYS_VERSION <= (3, 2)):
    mess = "Python Release 3.0 .. 3.2 are supported in this code branch."
    if SYS_VERSION >= (3, 6):
        mess += (
            "\nFor your Python, version %s, use the master branch."
            % sys.version[0:3]
        )
    elif SYS_VERSION > (3, 2):
        mess += (
            "\nFor your Python, version %s, use the python-3.3-3.5 branch."
            % sys.version[0:3]
        )
    elif (2, 4) <= SYS_VERSION <= (2, 7):
        mess += (
            "\nFor your Python, version %s, use the python-2.4-2.7 branch."
            % sys.version[0:3]
        )
    else:
        mess += (
            "\nThis package is not supported for Python version %s." % sys.version[0:3]
        )

    print(mess)
    raise Exception(mess)
"""
"""

import sys

from setuptools import find_packages, setup
>>>>>>> python-3.3-to-3.5

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

major = sys.version_info[0]
minor = sys.version_info[1]

if major != 3 or not 3 >= minor >= 6:
    sys.stderr.write("This installation medium is only for Python 3.3 to 3.5. You are running Python %s.%s.\n" % (major, minor))

if major == 3 and 6 <= minor <= 10:
    sys.stderr.write("Please install using xdis_36-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)
elif major == 3 and minor >= 11:
    sys.stderr.write("Please install using xdis-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
    sys.exit(1)
if major == 3 and 0 <= minor <= 2:
    sys.stderr.write("Please install using xdis_30-x.y.z.tar.gz from https://github.com/rocky/python-xdis/releases\n")
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
