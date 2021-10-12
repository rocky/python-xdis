#!/usr/bin/env python
""" Trivial helper program to bytecompile
"""
from xdis.version_info import PYTHON_VERSION_TRIPLE
import os, sys, py_compile
assert len(sys.argv) == 2
path = sys.argv[1]
short = os.path.basename(path)
version = ".".join([str(v) for v in PYTHON_VERSION_TRIPLE[:2]])
if hasattr(sys, 'pypy_version_info'):
    cfile =  "bytecode_pypy%s/%s" % (version, short) + 'c'
else:
    cfile =  "bytecode_%s/%s" % (version, short) + 'c'
print("byte-compiling %s to %s" % (path, cfile))
py_compile.compile(path, cfile)
os.system("../bin/pydisasm %s" % cfile)
