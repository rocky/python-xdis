#!/usr/bin/env python
# Mode: -*- python -*-
# Copyright (c) 2015-2021, 2023-2025 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#
import getopt
import os
import os.path as osp
import sys

from xdis import disassemble_file
from xdis.version import __version__
from xdis.version_info import PYTHON_VERSION_STR, PYTHON_VERSION_TRIPLE

FORMATS = ("xasm", "bytes", "classic", "dis", "extended", "extended-bytes", "header")

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
  -F | --format {xasm | bytes | classic | dis | extended | extended-bytes | header}
                     Specifiy assembly output format
  -V | --version     Show version and stop
  -S | --show-source Show source code when it is available
  -h | --help        Show this message
  -m | --method      Specify which specific methods or functions to show.
                     If omitted all, functions are shown.
                     Can be given multiple times.
  -x | --show-file-offsets
                     Show bytecode file hex addresses for the start of each code object

Examples:
  pydisasm foo.pyc
  pydisasm foo.py           # same thing as above but find the file
  pydisasm -F xasm foo.py   # produce xasm assembler-friendly output
  pydisasm foo.pyc bar.pyc  # disassemble foo.pyc and bar.pyc

"""

PATTERNS = ("*.pyc", "*.pyo")

def main():
def main(format: str, method: tuple, show_source: bool, show_file_offsets, files):
    """Disassembles a Python bytecode file.

    We handle bytecode for virtually every release of Python and some releases of PyPy.
    The version of Python in the bytecode doesn't have to be the same version as
    the Python interpreter used to run this program. For example, you can disassemble Python 3.6.9
    bytecode from Python 2.7.15 and vice versa.
    """
    Usage_short = """usage:
   %s FILE...
Type -h for for full help.""" % program

    if not ((2, 4) <= PYTHON_VERSION_TRIPLE < (3, 0)):
        mess = "This code works on 2.4 to 2.7; you have %s."
        if (3, 0) <= PYTHON_VERSION_TRIPLE <= (3, 2):
            mess += (
                " Code that works for %s can be found in the python-3.0-to-3.3 branch\n"
            )
        elif (3, 3) <= PYTHON_VERSION_TRIPLE <= (3, 5):
            mess += " Code that works for %s can be found in the python-3.3-to-3.10 branch\n"
        elif (3, 6) <= PYTHON_VERSION_TRIPLE <= (3, 10):
            mess += " Code that works for %s can be found in the python-3.6 branch\n"
        elif (3, 11) <= PYTHON_VERSION_TRIPLE:
            mess += " Code that works for %s can be found in the master branch\n"
        sys.stderr.write(mess % PYTHON_VERSION_STR)
        sys.exit(2)

    if len(sys.argv) == 1:
        sys.stderr.write("No file(s) given..\n")
        sys.stderr.write(Usage_short)
        sys.exit(1)

    try:
        opts, files = getopt.getopt(
            sys.argv[1:],
            "hVF:m:xS",
            ["help", "version", "format", "method", "show-file-offsets", "show-source"],
        )
    except getopt.GetoptError:
        sys.stderr.write("%s\n" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    format = "classic"
    show_source = False
    show_file_offsets=False
    methods = []
    for opt, val in opts:
        if opt in ("-h", "--help"):
            print(__doc__)
            sys.exit(1)
        elif opt in ("-V", "--version"):
            print("%s %s" % (program, __version__))
            sys.exit(0)
        elif opt in ("-F", "--format"):
            if val not in FORMATS:
                sys.stderr.write(
                    ("Invalid format option %s\n" + "Should be one of: %s\n")
                    % (val, ", ".join(FORMATS))
                )
                sys.exit(2)
            format = val
        elif opt in ("-m", "--method"):
            methods.append(val)
        elif opt in ("-S", "--show-source"):
            show_source = True
        elif opt in ("-x", "--show-file-offsets"):
            show_file_offsets = True
        else:
            print(opt)
            sys.stderr.write(Usage_short)
            sys.exit(1)

    rc = 0
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

        try:
            disassemble_file(
                path,
                sys.stdout,
                format,
                show_source=show_source,
                methods=methods,
                save_file_offsets=show_file_offsets,
            )
        except (ImportError, NotImplementedError, ValueError):
            print(sys.exc_info()[1])
            rc = 3
    sys.exit(rc)


if __name__ == "__main__":
    main()
