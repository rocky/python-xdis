# Copyright (c) 2016-2017 by Rocky Bernstein
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

from xdis import IS_PYPY
from xdis.bytecode import Bytecode
from xdis.code import iscode
from xdis.load import check_object_path, load_module
from xdis.util import format_code_info
from xdis.version import VERSION
from xdis.op_imports import op_imports

def get_opcode(version, is_pypy):
    # Set up disassembler with the right opcodes
    lookup = str(version)
    if is_pypy:
        lookup += 'pypy'
    if lookup in op_imports.keys():
        return op_imports[lookup]
    if is_pypy:
        pypy_str = ' for pypy'
    else:
        pypy_str = ''
    raise TypeError("%s is not a Python version%s I know about" %
                    (version, pypy_str))

def disco(bytecode_version, co, timestamp, out=sys.stdout,
          is_pypy=False, magic_int=None, source_size=None,
          header=True, asm_format=False, dup_lines=False):
    """
    diassembles and deparses a given code block 'co'
    """

    assert iscode(co)

    # store final output stream for case of error
    real_out = out or sys.stdout
    co_pypy_str = 'PyPy ' if is_pypy else ''
    run_pypy_str = 'PyPy ' if IS_PYPY else ''
    if header:
        real_out.write(('# pydisasm version %s\n# %sPython bytecode %s%s'
                   '\n# Disassembled from %sPython %s\n') %
                  (VERSION, co_pypy_str, bytecode_version,
                   " (%d)" % magic_int if magic_int else "",
                   run_pypy_str, '\n# '.join(sys.version.split('\n'))))
    if timestamp > 0:
        value = datetime.datetime.fromtimestamp(timestamp)
        real_out.write('# Timestamp in code: %d' % timestamp)
        real_out.write(value.strftime(' (%Y-%m-%d %H:%M:%S)\n')
)
    if source_size:
        real_out.write('# Source code size mod 2**32: %d bytes\n' % source_size)

    if co.co_filename and not asm_format:
        real_out.write(format_code_info(co, bytecode_version) + "\n")
        pass

    opc = get_opcode(bytecode_version, is_pypy)

    if asm_format:
        disco_loop_asm_format(opc, bytecode_version, co, real_out)
    else:
        queue = deque([co])
        disco_loop(opc, bytecode_version, queue, real_out)


def disco_loop(opc, version, queue, real_out, dup_lines=False):
    """Disassembles a queue of code objects. If we discover
    another code object which will be found in co_consts, we add
    the new code to the list. Note that the order of code discovery
    is in the order of first encountered which is not amenable for
    the format used by a disassembler where code objects should
    be defined before using them in other functions.
    However this is not recursive and will overall lead to less
    memory consumption at run time.
    """

    while len(queue) > 0:
        co = queue.popleft()
        if co.co_name != '<module>':
            real_out.write("\n" + format_code_info(co, version) + "\n")

        bytecode = Bytecode(co, opc, dup_lines=dup_lines)
        real_out.write(bytecode.dis() + "\n")

        for c in co.co_consts:
            if iscode(c):
                queue.append(c)
            pass
        pass

def disco_loop_asm_format(opc, version, co, real_out):
    """Produces disassembly in a format more conducive to
    automatic assembly by producing inner modules before they are
    used by outer ones. Since this is recusive, we'll
    use more stack space at runtime.
    """
    for c in co.co_consts:
        if iscode(c):
            disco_loop_asm_format(opc, version, c, real_out)
        pass

    if co.co_name != '<module>' or co.co_filename:
        real_out.write("\n" + format_code_info(co, version) + "\n")

    bytecode = Bytecode(co, opc, dup_lines=True)
    real_out.write(bytecode.dis(asm_format=True) + "\n")

def disassemble_file(filename, outstream=sys.stdout, asm_format=False):
    """
    disassemble Python byte-code file (.pyc)

    If given a Python source file (".py") file, we'll
    try to find the corresponding compiled object.
    """
    filename = check_object_path(filename)
    version, timestamp, magic_int, co, is_pypy, source_size  = load_module(filename)
    disco(version, co, timestamp, outstream, is_pypy, magic_int, source_size,
          asm_format=asm_format)
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
