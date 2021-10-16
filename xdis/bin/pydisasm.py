#!/usr/bin/env python
# Mode: -*- python -*-
# Copyright (c) 2015-2021 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#
import sys, os, getopt
import os.path as osp

from xdis.version import __version__
from xdis.version_info import PYTHON_VERSION_STR, PYTHON_VERSION_TRIPLE
from xdis import disassemble_file

FORMATS=("xasm", "bytes", "classic", "extended", "extended-bytes", "header")

program, ext = os.path.splitext(os.path.basename(__file__))

__doc__ = """
Usage:
  pydisasm [OPTIONS]... FILE
  pydisasm [--help | -h | -V | --version]

Disassembles a Python bytecode file.

We handle bytecode for virtually every release of Python and some releases of PyPy.
The version of Python in the bytecode doesn't have to be the same version as
the Python interpreter used to run this program. For example, you can disassemble Python 3.6.1
bytecode from Python 2.7.13 and vice versa.

Options:
  -F | --format {xasm | bytes | classic | extended | extended-bytes | header}
                     specifiy assembly output format
  -V | --version     show version and stop
  -h | --help        show this message
  --header           Show only the module header information

Examples:
  pydisasm foo.pyc
  pydisasm foo.py           # same thing as above but find the file
  pydisasm -F xasm foo.py    # produce xasm assembler-friendly output
  pydisasm foo.pyc bar.pyc  # disassemble foo.pyc and bar.pyc

"""

PATTERNS = ('*.pyc', '*.pyo')

def main():
    """Disassembles a Python bytecode file.

    We handle bytecode for virtually every release of Python and some releases of PyPy.
    The version of Python in the bytecode doesn't have to be the same version as
    the Python interpreter used to run this program. For example, you can disassemble Python 3.6.9
    bytecode from Python 2.7.15 and vice versa.
    """
    Usage_short = """usage:
   %s FILE...
Type -h for for full help.""" % program

    if not ((2, 4) <= PYTHON_VERSION_TRIPLE < (2, 8)):
        mess = "This code works on 2.4 to 2.17."
        if (3, 6) <= PYTHON_VERSION_TRIPLE <= (3, 11):
            mess += " Code that works for %s can be found in the master.4 branch\n"
        elif (3, 1) <= PYTHON_VERSION_TRIPLE <= (3, 2):
            mess += " Code that works for %s can be found in the python-3.1 branch\n"
        elif (3, 3) <= PYTHON_VERSION_TRIPLE <= (3, 5):
            mess += " Code that works for %s can be found in the python-3.3 branch\n"
        sys.stderr.write(mess % PYTHONVERSION_STR)
        sys.exit(2)

    if len(sys.argv) == 1:
        sys.stderr.write("No file(s) given..\n")
        sys.stderr.write(Usage_short)
        sys.exit(1)

    try:
        opts, files = getopt.getopt(sys.argv[1:], 'hVUHF:',
                                    ['help', 'version', 'header', 'format'])
    except getopt.GetoptError, e:
        sys.stderr.write('%s: %s\n' % (os.path.basename(sys.argv[0]), e))
        sys.exit(-1)

    format = "classic"
    asm, header = False, False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            sys.exit(1)
        elif opt in ('-V', '--version'):
            print("%s %s" % (program, VERSION))
            sys.exit(0)
        elif opt in ('-H', '--header'):
            header = True
        elif opt in ('--no-header'):
            header = False
        elif opt in ('-F', '--format'):
            if val not in FORMATS:
                sys.stderr.write(("Invalid format option %s\n" +
                                 "Should be one of: %s\n") %
                                 (val, ", ".join(FORMATS)))
                sys.exit(2)
            format = val
        else:
            print(opt)
            sys.stderr.write(Usage_short)
            sys.exit(1)

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

if __name__ == '__main__':
    main()
