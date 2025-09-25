"""xdis packaging information"""

import os.path as osp

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

# Python-version | package | last-version |
# -----------------------------------------
# 2.5            | pip     |  1.1         |
# 2.6            | pip     |  1.5.6       |
# 2.7            | pip     | 19.2.3       |
# 2.7            | pip     |  1.2.1       |
# 3.1            | pip     |  1.5.6       |
# 3.2            | pip     |  7.1.2       |
# 3.3            | pip     | 10.0.1       |
# 3.4            | pip     | 19.1.1       |

# Things that change more often go here.
copyright = """
Copyright (C) 2015-2020, 2023-2025 Rocky Bernstein <rb@dustyfeet.com>.
"""

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Debuggers",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# The rest in alphabetic order
author = "Rocky Bernstein, Hartmut Goebel and others"
author_email = "rb@dustyfeet.com"
entry_points = {
    "console_scripts": [
        "pydisasm=xdis.bin.pydisasm:main",
    ]
}
ftp_url = None
install_requires = []
license = "GPL-2.0"
mailing_list = "python-debugger@googlegroups.com"
modname = "xdis"

packages = ["xdis"]
py_modules = None

python_requires = ">=2.4,<3.0"

# setup_requires     = ['pytest-runner']
scripts = ["bin/pydisasm.py"]
short_desc = "Python cross-version byte-code disassembler and marshal routines"
tests_require = ["pytest"]
web = "https://github.com/rocky/python-xdis/"

# tracebacks in zip files are funky and not debuggable
zip_safe = True


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(osp.join(srcdir, *rnames)).read()


# Get info from files; set: long_description and VERSION
long_description = read("README.rst") + "\n"
exec(read("xdis/version.py"))
