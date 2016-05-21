# Copyright (c) 2015-2016 by Rocky Bernstein
"""
CPython independent disassembly routines

There are two reasons we can't use Python's built-in routines
from dis. First, the bytecode we are extracting may be from a different
version of Python (different magic number) than the version of Python
that is doing the extraction.

Second, we need structured instruction information for the
(de)-parsing step. Python 3.4 and up provides this, but we still do
want to run on Python 2.7.
"""

# Note: we tend to eschew new Python 3 things, and even future
# imports so this can run on older Pythons. This is
# intended to be a more cross-version Python program

import sys
from collections import deque

import pyxdis

from pyxdis import PYTHON_VERSION
from pyxdis.bytecode import Bytecode
from pyxdis.code import iscode
from pyxdis.opcodes import (opcode_25, opcode_26, opcode_27, opcode_30, opcode_31,
                            opcode_32, opcode_33, opcode_34, opcode_35)
from pyxdis.load import check_object_path, load_module
from pyxdis.util import format_code_info

## FIXME: this comes from Python's dis.py
## Isolate it?

def get_opcode(version):
    # Set up disassembler with the right opcodes
    if version == 2.5:
        return opcode_25
    elif version == 2.6:
        return opcode_26
    elif version == 2.7:
        return opcode_27
    elif version == 3.0:
        return opcode_30
    elif version == 3.1:
        return opcode_31
    elif version == 3.2:
        return opcode_32
    elif version == 3.3:
        return opcode_33
    elif version == 3.4:
        return opcode_34
    elif version == 3.5:
        return opcode_35
    else:
        raise TypeError("%s is not a Python version I know about" % version)

def disco(version, co, out=sys.stdout):
    """
    diassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    # store final output stream for case of error
    real_out = out or sys.stdout
    out.write('# Python bytecode %s (disassembled from Python %s)\n' %
              (version, PYTHON_VERSION))
    if co.co_filename:
        out.write(format_code_info(co, version) + "\n")

    opc = get_opcode(version)

    queue = deque([co])
    disco_loop(opc, version, queue, real_out)


def disco_loop(opc, version, queue, real_out):
    while len(queue) > 0:
        co = queue.popleft()
        if co.co_name != '<module>':
            real_out.write("\n" + format_code_info(co, version) + "\n")
        real_out.write("\n" + format_code_info(co, version) + "\n")

        bytecode = Bytecode(co, opc)
        real_out.write(bytecode.dis() + "\n")

        for instr in bytecode.get_instructions(co):
            if iscode(instr.argval):
                queue.append(instr.argval)
            pass
        pass

def disassemble_file(filename, outstream=sys.stdout):
    """
    disassemble Python byte-code file (.pyc)

    If given a Python source file (".py") file, we'll
    try to find the corresponding compiled object.
    """
    filename = check_object_path(filename)
    version, timestamp, magic_int, co = load_module(filename)
    disco(version, co, outstream)
    co = None

def _test():
    """Simple test program to disassemble a file."""
    argc = len(sys.argv)
    if argc != 2:
        if argc == 1 and pyxdis.PYTHON3:
            fn = __file__
        else:
            sys.stderr.write("usage: %s [-|CPython compiled file]\n" % __file__)
            sys.exit(2)
    else:
        fn = sys.argv[1]
    disassemble_file(fn, native=True)

if __name__ == "__main__":
    _test()
