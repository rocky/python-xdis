# Mode: -*- python -*-
# Copyright (c) 2015-2019 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#
import sys, os, getopt
import os.path as osp

from xdis.version import VERSION
from xdis import PYTHON_VERSION
from xdis.main import disassemble_file

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
  -a | --asm         produce assembly output more suitable for modification
  -V | --version     show version and stop
  -h | --help        show this message
  --header           Show only the module header information

Examples:
  pydisasm foo.pyc
  pydisasm foo.py           # same thing as above but find the file
  pydisasm --asm foo.py     # produce assembler-friendly output
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

    if not (2.4 <= PYTHON_VERSION <= 3.8):
        sys.stderr.write("This works on Python version 2.4..3.8; have %s\n"
                         % PYTHON_VERSION)
        sys.exit(1)

    if len(sys.argv) == 1:
        sys.stderr.write("No file(s) given..\n")
        sys.stderr.write(Usage_short)
        sys.exit(1)

    try:
        opts, files = getopt.getopt(sys.argv[1:], 'hVUHa',
                                    ['help', 'version', 'header', 'asm', 'noasm'])
    except getopt.GetoptError, e:
        sys.stderr.write('%s: %s\n' % (os.path.basename(sys.argv[0]), e))
        sys.exit(-1)

    asm, header = False, False
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            sys.exit(1)
        elif opt in ('-V', '--version'):
            print("%s %s" % (program, VERSION))
            sys.exit(0)
        elif opt in ('-a', '--asm'):
            asm = True
        elif opt in ('--noasm'):
            asm = False
        elif opt in ('-H', '--header'):
            header = True
        elif opt in ('--no-header'):
            header = False
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
        elif osp.getsize(path) < 50:
            sys.stderr.write(
                "File name: '%s (%d bytes)' is too short to be a valid pyc file\n"
                % (path, osp.getsize(path))
            )
            continue

        disassemble_file(path, sys.stdout, asm, header)
    return

if __name__ == '__main__':
    main()
