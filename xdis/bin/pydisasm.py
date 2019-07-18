# Mode: -*- python -*-
# Copyright (c) 2015-2019 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#
from __future__ import print_function
import sys, os
import click
import os.path as osp

from xdis.version import VERSION
from xdis import PYTHON_VERSION
from xdis.main import disassemble_file

program, ext = os.path.splitext(os.path.basename(__file__))

PATTERNS = ('*.pyc', '*.pyo')

@click.command()
@click.option("--asm/--noasm", default=False,
              help='Produce output suitable for the xasm assembler')
@click.option("--show-bytes/--noshow-bytes", default=False,
              help='include bytecode bytes in output')
@click.version_option(version=VERSION)
@click.option("--header/--no-header", default=False,
              help='Show only the module header information')
@click.argument('files', nargs=-1, type=click.Path(readable=True), required=True)
def main(asm, show_bytes, header, files):
    """Disassembles a Python bytecode file.

    We handle bytecode for virtually every release of Python and some releases of PyPy.
    The version of Python in the bytecode doesn't have to be the same version as
    the Python interpreter used to run this program. For example, you can disassemble Python 3.6.1
    bytecode from Python 2.7.13 and vice versa.
    """
    Usage_short = """usage:
   %s [--asm] -i FILE...
   %s --version
Type -h for for full help.""" % (program, program)


    if not (2.5 <= PYTHON_VERSION <= 3.8):
        sys.stderr(print("This works on Python version 2.5..3.8; have %s" % PYTHON_VERSION))

    if not len(files):
        sys.stderr.write("No file(s) given..\n")
        print(Usage_short, file=sys.stderr)
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
            sys.stderr.write("File name: '%s (%d bytes)' is too short to be a valid pyc file\n" % (path, osp.getsize(path)))
            continue

        disassemble_file(path, sys.stdout, asm, header, show_bytes)
    return

if __name__ == '__main__':
    main(sys.argv[1:])
