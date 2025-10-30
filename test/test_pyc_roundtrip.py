#!/usr/bin/env python
# (C) Copyright 2025 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
test_pyc_roundtrip.py -- roundtrip check of bytecode_*/roundtrip/*.py{c,o} files

Usage-Examples:

  # disassemble base set of python 2.7 byte-compiled files
  test_pyc_roundtrip.py --base-2.7

  # Just deompile the longer set of files
  test_pyc_roundtrip.py --ok-2.7

Adding own test-trees:

Step 1) Edit this file and add a new entry to 'test_options', eg.
  test_options['mylib'] = ('/usr/lib/mylib', PYOC, 'mylib')
Step 2: Run the test:
  test_pyc_roundtrip.py --mylib	  # decompile 'mylib'
  test_pyc_roundtrip.py --mylib --verify # decompile verify 'mylib'
"""

from __future__ import print_function

import getopt
import os
import sys
import tempfile
import time
from fnmatch import fnmatch

from xdis.roundtrip_pyc import roundtrip_pyc


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)


src_dir = get_srcdir()


# ----- configure this for your needs

target_base = tempfile.mkdtemp(prefix="py-dis-")

PY = ("*.py",)
PYC = ("*.pyc",)
PYO = ("*.pyo",)
PYOC = ("*.pyc", "*.pyo")

test_options = {
    # name:   (src_basedir, pattern, output_base_suffix, python_version)
    "test": ("test", PYC, "test"),
    "base-2.7": (
        os.path.join(src_dir, "base_tests", "python2.7"),
        PYOC,
        "base_2.7",
        2.7,
    ),
}

for vers in (
    1.0,
    1.1,
    1.2,
    1.3,
    1.4,
    1.5,
    1.6,
    2.1,
    2.2,
    2.3,
    2.4,
    2.5,
    "2.5dropbox",
    2.6,
    2.7,
    3.0,
    3.1,
    3.2,
    3.3,
    3.4,
    3.5,
    "3.2pypy",
    "2.7pypy",
    3.6,
    3.7,
    3.8,
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
):
    bytecode = "bytecode_%s/roundtrip_pyc" % vers
    key = "bytecode-%s" % vers
    test_options[key] = (os.path.join(src_dir, bytecode), PYC, bytecode, vers)
    key = f"{vers}"

for vers, vers_dot in (
    (35, 3.5),
    (36, 3.6),
    (37, 3.7),
    (38, 3.8),
    (39, 3.9),
    (310, 3.10),
    (311, 3.11),
    (312, 3.12),
    (313, 3.13),
):
    bytecode = "bytecode_pypy%s" % vers
    key = "bytecode-pypy%s" % vers
    test_options[key] = (os.path.join(src_dir, bytecode), PYOC, bytecode, vers_dot)
    key = "bytecode-pypy%s" % vers_dot
    test_options[key] = (os.path.join(src_dir, bytecode), PYOC, bytecode, vers_dot)


# -----


def help():
    print(
        """Usage-Examples:

  # roundtrip pyc check Python 2.7:
  test_pyc_roundtrip.py --bytecode-2.7
"""
    )
    sys.exit(1)


def do_tests(src_dir, obj_patterns, opts):
    def file_matches(files, root, basenames, patterns):
        files.extend(
            [
                os.path.normpath(os.path.join(root, n))
                for n in basenames
                for pat in patterns
                if fnmatch(n, pat)
            ]
        )

    files = []
    # Change directories so use relative rather than
    # absolute paths. This speeds up things, and allows
    # main() to write to a relative-path destination.
    cwd = os.getcwd()
    os.chdir(src_dir)

    for root, _dirs, basenames in os.walk("."):
        # Turn root into a relative path
        dirname = root[2:]  # 2 = len('.') + 1
        file_matches(files, dirname, basenames, obj_patterns)

    if not files:
        sys.stderr.write("Didn't come up with any files to test! Try with --compile?\n")
        exit(1)

    os.chdir(cwd)
    files.sort()

    if opts["start_with"]:
        try:
            start_with = files.index(opts["start_with"])
            files = files[start_with:]
            print(">>> starting with file", files[0])
        except ValueError:
            pass

    print(time.ctime())
    print("Source directory: ", src_dir)
    cwd = os.getcwd()
    os.chdir(src_dir)
    failure_count = 0
    try:
        for infile in files:
            failure_count += roundtrip_pyc(infile, unlink_on_success=False, verbose=test_opts["verbose"])

    except (KeyboardInterrupt, OSError):
        print()
        exit(1)
    finally:
        os.chdir(cwd)

    n = len(files)
    print(
        "Processed %s files: %d good, and %d bad."
        % (n, n - failure_count, failure_count)
    )
    return failure_count


if __name__ == "__main__":
    test_dirs = []
    checked_dirs = []
    start_with = None

    test_options_keys = list(test_options.keys())
    test_options_keys.sort()
    opts, args = getopt.getopt(
        sys.argv[1:],
        "",
        ["start-with=", "all", "quiet", "no-rm"] + test_options_keys,
    )
    if not opts:
        help()

    test_opts = {
        "start_with": None,
        "rmtree": True,
    }

    test_opts["verbose"] = True
    for opt, val in opts:
        if opt == "--start-with":
            test_opts["start_with"] = val
        elif opt == "--no-rm":
            test_opts["rmtree"] = False
        elif opt == "--quiet":
            test_opts["verbose"] = False
        elif opt[2:] in test_options_keys:
            test_dirs.append(test_options[opt[2:]])
        elif opt == "--all":
            for val in test_options_keys:
                test_dirs.append(test_options[val])
        else:
            help()
            pass
        pass

    last_compile_version = None
    for src_dir, pattern, target_dir, compiled_version in test_dirs:
        if os.path.isdir(src_dir):
            checked_dirs.append([src_dir, pattern, target_dir])
        else:
            sys.stderr.write(f"Can't find directory {src_dir}. Skipping\n")
            continue
        last_compile_version = compiled_version
        pass

    if not checked_dirs:
        sys.stderr.write("No directories found to check\n")
        sys.exit(1)

    test_opts["compiled_version"] = last_compile_version

    for src_dir, pattern, target_dir in checked_dirs:
        do_tests(src_dir, pattern, test_opts)
