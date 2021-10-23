# Mode: -*- python -*-
# Copyright (c) 2015-2021 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#
from __future__ import print_function
import sys, os
import click
import os.path as osp

from xdis.version import __version__
from xdis.version_info import PYTHON_VERSION_STR, PYTHON_VERSION_TRIPLE
from xdis import disassemble_file

program, ext = os.path.splitext(os.path.basename(__file__))

PATTERNS = ("*.pyc", "*.pyo")

if click.__version__ >= "7.":
    case_sensitive = {"case_sensitive": False}
else:
    case_sensitive = {}


@click.command()
@click.option(
    "--format",
    "-F",
    type=click.Choice(
        ["xasm", "bytes", "classic", "extended", "extended-bytes", "header"],
        **case_sensitive
    ),
)
@click.version_option(version=__version__)
@click.argument("files", nargs=-1, type=click.Path(readable=True), required=True)
def main(format, files):
    """Disassembles a Python bytecode file.

    We handle bytecode for virtually every release of Python and some releases of PyPy.
    The version of Python in the bytecode doesn't have to be the same version as
    the Python interpreter used to run this program. For example, you can disassemble Python 3.6.9
    bytecode from Python 2.7.15 and vice versa.
    """
    if not ((2, 7) <= PYTHON_VERSION_TRIPLE < (3, 12)):
        mess = "This code works on 3.6 to 3.12."
        if (2, 4) <= PYTHON_VERSION_TRIPLE <= (2, 7):
            mess += " Code that works for %s can be found in the python-2.4 branch\n"
        elif (3, 1) <= PYTHON_VERSION_TRIPLE <= (3, 2):
            mess += " Code that works for %s can be found in the python-3.1 branch\n"
        elif (3, 3) <= PYTHON_VERSION_TRIPLE <= (3, 5):
            mess += " Code that works for %s can be found in the python-3.3 branch\n"
        sys.stderr.write(mess % PYTHON_VERSION_STR)
        sys.exit(2)

    for path in files:
        # Some sanity checks
        if not osp.exists(path):
            sys.stderr.write("File name: '%s' doesn't exist\n" % path)
            continue
        elif not osp.isfile(path):
            sys.stderr.write("File name: '%s' isn't a file\n" % path)
            continue
        elif osp.getsize(path) < 50 and not path.endswith(".py"):
            sys.stderr.write(
                "File name: '%s (%d bytes)' is too short to be a valid pyc file\n"
                % (path, osp.getsize(path))
            )
            continue

        disassemble_file(path, sys.stdout, format)
    return


if __name__ == "__main__":
    main(sys.argv[1:])
