#!/usr/bin/env python
# Mode: -*- python -*-
#
# Copyright (c) 2015-2016 by Rocky Bernstein <rb@dustyfeet.com>
#
import sys, os, getopt

from xdis.version import VERSION
from xdis import PYTHON_VERSION
from xdis.main import disassemble_file

program, ext = os.path.splitext(os.path.basename(__file__))

__doc__ = """
Usage:
  pydisasm [OPTIONS]... FILE
  pydisasm [--help | -h | -V | --version]

Examples:
  pydisasm foo.pyc
  pydisasm foo.py    # same thing as above but find the file
  pydisasm foo.pyc bar.pyc  # disassemble foo.pyc and bar.pyc

Options:
  -V | --version     show version and stop
  -h | --help        show this message

"""

PATTERNS = ('*.pyc', '*.pyo')

def main():
    Usage_short = """usage: %s FILE...
Type -h for for full help.""" % program

    if not (2.4 <= PYTHON_VERSION <= 2.7):
        sys.stderr.write("This works on Python version 2.4..2.7; have %s\n" % PYTHON_VERSION)
        sys.stderr.write("Try master branch for 3.0+\n")

    if len(sys.argv) == 1:
        sys.stderr.write("No file(s) given\n")
        sys.stderr.write(Usage_short)
        sys.exit(1)

    try:
        opts, files = getopt.getopt(sys.argv[1:], 'hVU',
                                    ['help', 'version'])
    except getopt.GetoptError(e):
        sys.stderr.write('%s: %s\n' % (os.path.basename(sys.argv[0]), e))
        sys.exit(-1)

    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            sys.exit(1)
        elif opt in ('-V', '--version'):
            print("%s %s" % (program, VERSION))
            sys.exit(0)
        else:
            print(opt)
            sys.stderr.write(Usage_short)
            sys.exit(1)

    for file in files:
        if os.path.exists(files[0]):
            disassemble_file(file, sys.stdout)
        else:
            sys.stderr.write("Can't read %s - skipping\n" % files[0])
            pass
        pass
    return

if __name__ == '__main__':
    main()
