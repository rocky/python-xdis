# Copyright (c) 2016 by Rocky Bernstein
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

import datetime, sys
from collections import deque

import xdis

from xdis import PYTHON_VERSION, IS_PYPY
from xdis.bytecode import Bytecode
from xdis.code import iscode
from xdis.load import check_object_path, load_module
from xdis.util import format_code_info

def get_opcode(version, is_pypy):
    # Set up disassembler with the right opcodes
    # Is there a better way?
    if version < 3.0:
        if version <= 2.3:
            if version == 1.5:
                from xdis.opcodes import opcode_15
                return opcode_15
            elif version == 2.0:
                from xdis.opcodes import opcode_20
                return opcode_20
            elif version == 2.1:
                from xdis.opcodes import opcode_21
                return opcode_21
            elif version == 2.2:
                from xdis.opcodes import opcode_22
                return opcode_22
            elif version == 2.3:
                from xdis.opcodes import opcode_23
                return opcode_23
            pass
        else:
            if version == 2.4:
                from xdis.opcodes import opcode_24
                return opcode_24
            elif version == 2.5:
                from xdis.opcodes import opcode_25
                return opcode_25
            elif version == 2.6:
                if is_pypy:
                    from xdis.opcodes import opcode_pypy26
                    return opcode_pypy26
                else:
                    from xdis.opcodes import opcode_26
                    return opcode_26
            elif version == 2.7:
                if is_pypy:
                    from xdis.opcodes import opcode_pypy27
                    return opcode_pypy27
                else:
                    from xdis.opcodes import opcode_27
                    return opcode_27
                pass
            pass
    else:
        if version < 3.3:
            if version == 3.0:
                from xdis.opcodes import opcode_30
                return opcode_30
            elif version == 3.1:
                from xdis.opcodes import opcode_31
                return opcode_31
            elif version == 3.2:
                from xdis.opcodes import opcode_32
                return opcode_32
        else:
            if version == 3.3:
                from xdis.opcodes import opcode_33
                return opcode_33
            elif version == 3.4:
                from xdis.opcodes import opcode_34
                return opcode_34
            elif version == 3.5:
                from xdis.opcodes import opcode_35
                return opcode_35
            elif version == 3.6:
                from xdis.opcodes import opcode_36
                return opcode_36
    raise TypeError("%s is not a Python version I know about" % version)

def disco(version, co, timestamp, out=sys.stdout,
          is_pypy=False, magic_int=None, source_size=None):
    """
    diassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    # store final output stream for case of error
    real_out = out or sys.stdout
    co_pypy_str = 'PyPy ' if is_pypy else ''
    run_pypy_str = 'PyPy ' if IS_PYPY else ''
    out.write('# %sPython bytecode %s%s disassembled from %sPython %s\n' %
              (co_pypy_str, version,
               " (%d)" % magic_int if magic_int else "",
               run_pypy_str, PYTHON_VERSION))
    if timestamp > 0:
        value = datetime.datetime.fromtimestamp(timestamp)
        out.write(value.strftime('# Timestamp in code: '
                                 '%Y-%m-%d %H:%M:%S\n'))
    if source_size:
        out.write(value.strftime('# Source code size mod 2**32: %d\n'
                                 % source_size))


    if co.co_filename:
        out.write(format_code_info(co, version) + "\n")
        pass

    opc = get_opcode(version, is_pypy)

    queue = deque([co])
    disco_loop(opc, version, queue, real_out)


def disco_loop(opc, version, queue, real_out):
    while len(queue) > 0:
        co = queue.popleft()
        if co.co_name != '<module>':
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
    version, timestamp, magic_int, co, is_pypy, source_size  = load_module(filename)
    disco(version, co, timestamp, outstream, is_pypy, magic_int, source_size)
    # print co.co_filename
    return filename, co, version, timestamp, magic_int

def _test():
    """Simple test program to disassemble a file."""
    argc = len(sys.argv)
    if argc != 2:
        if argc == 1 and xdis.PYTHON3:
            fn = __file__
        else:
            sys.stderr.write("usage: %s [-|CPython compiled file]\n" % __file__)
            sys.exit(2)
    else:
        fn = sys.argv[1]
    disassemble_file(fn)

if __name__ == "__main__":
    _test()
