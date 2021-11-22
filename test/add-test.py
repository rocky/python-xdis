#!/usr/bin/env python
""" Trivial helper program to bytecompile
"""
import os, sys, py_compile
if len(sys.argv) != 2:
    print("Usage: add-test.py *byte-compiled-file*")
    sys.exit(1)

if len(sys.argv) == 3:
    optimize = int(sys.argv[2])
else:
    optimize = 2

from xdis.version_info import version_tuple_to_str
path = sys.argv[1]
short = os.path.basename(path)

if hasattr(sys, 'pypy_version_info'):
    version = version_tuple_to_str(end=2, delimiter="")
    cfile = "bytecode_pypy%s/%s.pypy%s.pyc" % (version, short, version)
else:
    version = version_tuple_to_str(end=2)
    cfile = "bytecode_%s/%s.pyc" % (version, short)

print("byte-compiling %s to %s" % (path, cfile))
py_compile.compile(path, cfile)
os.system("../bin/pydisasm %s" % cfile)
