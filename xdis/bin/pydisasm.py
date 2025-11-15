# Mode: -*- python -*-
# Copyright (c) 2015-2021, 2025 by Rocky Bernstein <rb@dustyfeet.com>
#
# Note: we can't start with #! because setup.py bdist_wheel will look for that
# and change that into something that's not portable. Thank you, Python!
#
#

import os
import os.path as osp
import sys

import click

from xdis import disassemble_file
from xdis.version import __version__
from xdis.version_info import PYTHON_VERSION_STR, PYTHON_VERSION_TRIPLE

program, ext = os.path.splitext(os.path.basename(__file__))

PATTERNS = ("*.pyc", "*.pyo")

@click.command()
@click.option(
    "--format",
    "-F",
    type=click.Choice(
        ["xasm", "bytes", "classic", "dis", "extended", "extended-bytes", "header"],
    ),
    help="Select disassembly style.",
)
@click.option(
    "--method",
    "-m",
    metavar="FUNCTION-OR-METHOD",
    multiple=True,
    type=str,
    help=(
        "Specify which specific methods or functions to show. "
        "If omitted all, functions are shown. "
        "Can be given multiple times."
    ),
)
@click.option(
    "--show-source/--no-show-source",
    "-S",
    help="Intersperse Python source text from linecache if available.",
)
@click.option(
    "--show-file-offsets/--no-show-file_offsets",
    "-x",
    help="Show bytecode file hex addresses for the start of each code object.",
)
@click.version_option(version=__version__)
@click.argument("files", nargs=-1, type=click.Path(readable=True), required=True)
def main(format: str, method: tuple, show_source: bool, show_file_offsets, files):
    """Disassembles a Python bytecode file.

    We handle bytecode for virtually every release of Python and some releases of PyPy.
    The version of Python in the bytecode doesn't have to be the same version as
    the Python interpreter used to run this program. For example, you can disassemble Python 3.6.9
    bytecode from Python 2.7.15 and vice versa.
    """
    if not ((3, 0) <= PYTHON_VERSION_TRIPLE < (3, 3)):
        mess = "This code works on 3.0 to 3.2; you have %s."
        if (2, 4) <= PYTHON_VERSION_TRIPLE <= (2, 7):
            mess += " Code that works for %s can be found in the python-2.4-to-2.7 branch\n"
        elif (3, 3) <= PYTHON_VERSION_TRIPLE <= (3, 5):
            mess += " Code that works for %s can be found in the python-3.3-to-3.10 branch.\n"
        elif (3, 6) <= PYTHON_VERSION_TRIPLE <= (3, 10):
            mess += " Code that works for %s can be found in the python-3.6 branch.\n"
        elif (3, 11) <= PYTHON_VERSION_TRIPLE:
            mess += " Code that works for %s can be found in the master branch.\n"
        sys.stderr.write(mess % (PYTHON_VERSION_STR, PYTHON_VERSION_STR))
        sys.exit(2)

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
                methods=method,
                save_file_offsets=show_file_offsets,
            )
        except (ImportError, NotImplementedError, ValueError) as e:
            print(e)
            rc = 3
    sys.exit(rc)


if __name__ == "__main__":
    main(sys.argv[1:])
