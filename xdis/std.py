"""
Provide the same API as Python 3.x so xdis can be used as a drop in
replacement for dis. This will provide a dis module with support for the
Python version being run.

Why would you want this? The main reason is if you want a compatibility shim
for supporting the more advanced Python 3 dis API (being able to iterate through
opcodes, supplying a custom file to dump the dis to) across python versions, for
example:

    import xdis.std as dis

    # works in Python 2 and 3
    for op in dis.Bytecode('for i in range(10): pass'):
        print(op)

"""

# Used from the outside
from dis import hasconst, hasname, opmap, opname, EXTENDED_ARG, HAVE_ARGUMENT

# std
import sys
# local
from xdis import PYTHON_VERSION, IS_PYPY
from xdis.bytecode import (
    Bytecode as _Bytecode,
    Instruction as _Instruction,
)
if PYTHON_VERSION >= 3.6:
    import xdis.wordcode as xcode
else:
    import xdis.bytecode as xcode
from xdis.main import (
    get_opcode,
    disco as _disco,
)
from xdis.util import (
    code_info as _code_info,
    show_code as _show_code,
    pretty_flags as _pretty_flags,
)


opc = get_opcode(PYTHON_VERSION, IS_PYPY)


def _print(x, file=None):
    if file is None:
        print(x)
    else:
        file.write(str(x) + '\n')


class Bytecode(_Bytecode):
    """The bytecode operations of a piece of code

    Instantiate this with a function, method, string of code, or a code object
    (as returned by compile()).

    Iterating over this yields the bytecode operations as Instruction instances.
    """
    def __init__(self, x, first_line=None, current_offset=None):
        super(Bytecode, self).__init__(x, opc=opc, first_line=first_line, current_offset=current_offset)


def code_info(x):
    """Formatted details of methods, functions, or code."""
    return _code_info(x, PYTHON_VERSION)


def show_code(x, file=None):
    """Print details of methods, functions, or code to *file*.

    If *file* is not provided, the output is printed on stdout.
    """
    return _show_code(x, opc.version, file)


def pretty_flags(flags):
    """Return pretty representation of code flags."""
    return _pretty_flags(flags)


def dis(x=None, file=None):
    """Disassemble classes, methods, functions, generators, or code.

    With no argument, disassemble the last traceback.

    """
    _print(Bytecode(x).dis(), file)


def distb(tb=None, file=None):
    """Disassemble a traceback (default: last traceback)."""
    if tb is None:
        try:
            tb = sys.last_traceback
        except AttributeError:
            raise RuntimeError("no last traceback to disassemble")
        while tb.tb_next: tb = tb.tb_next
    disassemble(tb.tb_frame.f_code, tb.tb_lasti, file=file)


def disassemble(code, lasti=-1, file=None):
    """Disassemble a code object."""
    return disco(code, lasti, file)


def disco(code, lasti=-1, file=None):
    """Disassemble a code object."""
    return _disco(PYTHON_VERSION, code, timestamp=0, out=file, is_pypy=IS_PYPY, header=False)


def get_instructions(x, first_line=None):
    """Iterator for the opcodes in methods, functions or code

    Generates a series of Instruction named tuples giving the details of
    each operations in the supplied code.

    If *first_line* is not None, it indicates the line number that should
    be reported for the first source line in the disassembled code.
    Otherwise, the source line information (if any) is taken directly from
    the disassembled code object.
    """
    return Bytecode(x).get_instructions(x, first_line)


def findlinestarts(code):
    """Find the offsets in a byte code which are start of lines in the source.

    Generate pairs (offset, lineno) as described in Python/compile.c.

    """
    return xcode.findlinestarts(code)


def findlabels(code):
    """Detect all offsets in a byte code which are jump targets.

    Return the list of offsets.

    """
    return xcode.findlabels(code, opc)


class Instruction(_Instruction):
    """Details for a bytecode operation

       Defined fields:
         opname - human readable name for operation
         opcode - numeric code for operation
         arg - numeric argument to operation (if any), otherwise None
         argval - resolved arg value (if known), otherwise same as arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (if any), otherwise None
         is_jump_target - True if other code jumps to here, otherwise False
    """
    def __init__(self, *args, **kwargs):
        kwargs['opc'] = opc
        super(Instruction, self).__init__(*args, **kwargs)
