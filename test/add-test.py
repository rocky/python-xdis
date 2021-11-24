#!/usr/bin/env python
""" Trivial helper program to byte compile and run an pydisasm on the bytecode file.
"""
import os, sys, py_compile
from xdis.version_info import version_tuple_to_str, PYTHON_VERSION_TRIPLE

if len(sys.argv) < 2:
    print("Usage: add-test.py *python-source*... [optimize-level]")
    sys.exit(1)

try:
    optimize = int(sys.argv[-1])
    assert sys.argv >= 3
    py_source = sys.argv[1:-1]
except:
    optimize = 2
    py_source = sys.argv[1:]

for path in py_source:
    short = os.path.basename(path)
    if hasattr(sys, 'pypy_version_info'):
        version = version_tuple_to_str(end=2, delimiter="")
        bytecode = "bytecode_pypy%s/%s.pypy%s.pyc" % (version, short, version)
    else:
        version = version_tuple_to_str(end=2)
        bytecode = "bytecode_%s/%s.pyc" % (version, short)

    print("byte-compiling %s to %s" % (path, bytecode))
    if PYTHON_VERSION_TRIPLE >= (3, 2):
        py_compile.compile(path, bytecode, optimize=optimize)
    else:
        py_compile.compile(path, bytecode)

    os.system("../bin/pydisasm %s" % bytecode)
