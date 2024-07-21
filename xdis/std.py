# (C) Copyright 2018 by Daniel Bradburn
# (C) Copyright 2018, 2020, 2023-2024 by Rocky Bernstein
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
Provide the same API as Python 3.x so xdis can be used as a drop-in
replacement for ``dis``.

This will provide ``dis`` module with support for the Python version being run.

Why would you want this? The main reason is if you want a compatibility shim
for supporting the more advanced Python3 dis API. That is, to be able to iterate through
opcodes, supplying a custom file to dump the dis to across python versions. For
example:

    import xdis.std as dis

    # works in Python 2 and 3
    for op in dis.Bytecode('for i in range(10): pass'):
        print(op)

There is also the ability to generate a std api for a specific version. For example:

    from xdis.std import make_std_api
    dis = make_std_api(2.4)
    # dis can now disassemble code objects from python 2.4

Version 'variants' are also supported, for example:

    from xdis.std import make_std_api
    dis = make_std_api(2.6, 'pypy')
    # dis can now disassemble pypy code objects from python 2.6

"""

# std
import sys

# xdis
from xdis import IS_GRAAL, IS_PYPY
from xdis.bytecode import Bytecode as _Bytecode, get_optype
from xdis.cross_dis import (
    code_info as _code_info,
    op_has_argument,
    pretty_flags as _pretty_flags,
    show_code as _show_code,
    xstack_effect as _stack_effect,
)
from xdis.disasm import disco as _disco
from xdis.instruction import Instruction as Instruction_xdis
from xdis.op_imports import get_opcode_module

PYPY = "pypy"
GRAAL = "Graal"
VARIANT = PYPY if IS_PYPY else None
VARIANT = GRAAL if IS_GRAAL else None


class _StdApi:
    def __init__(self, python_version=sys.version_info, variant=VARIANT):
        if python_version >= (3, 6):
            import xdis.wordcode as xcode
        else:
            import xdis.bytecode as xcode
        self.xcode = xcode

        self.opc = opc = get_opcode_module(python_version, variant)
        self.python_version_tuple = opc.version_tuple
        self.is_pypy = variant == PYPY
        self.is_graal = variant == GRAAL
        self.hasconst = opc.hasconst
        self.hasname = opc.hasname
        self.opmap = opc.opmap
        self.opname = opc.opname
        self.EXTENDED_ARG = opc.EXTENDED_ARG
        self.HAVE_ARGUMENT = opc.HAVE_ARGUMENT

        class Bytecode(_Bytecode):
            """The bytecode operations in a piece of code

            Instantiate this with a function, method, string of code, or a code object
            (as returned by compile()).

            Iterating over these yields a bytecode operation as Instruction instances.
            """

            def __init__(self, x, first_line=None, current_offset=None, opc=None):
                if opc is None:
                    opc = _std_api.opc
                _Bytecode.__init__(
                    self,
                    x,
                    opc=opc,
                    first_line=first_line,
                    current_offset=current_offset,
                )

        self.Bytecode = Bytecode

        class Instruction(Instruction_xdis):
            """Details for a bytecode operation

            Defined fields:
              opcode - numeric code for operation
              opname - human-readable name for operation
              arg - numeric argument to operation (if any), otherwise None
              argval - resolved arg value (if known), otherwise same as arg
              argrepr - human-readable description of operation argument
              offset - start index of operation within bytecode sequence
              starts_line - line started by this opcode (if any), otherwise None
              is_jump_target - True if other code jumps to here, otherwise False

              If 3.4 (and changed in 3.11) or greater
              positions
            """

            def __init__(
                self,
                opcode,
                opname,
                arg,
                argval,
                argrepr,
                offset,
                starts_line,
                is_jump_target,
                positions=None,
                **kwargs
            ):
                has_args = op_has_argument(opcode, self.opc)
                if "has_args" in kwargs:
                    assert has_args == kwargs.pop("has_args")
                optype = get_optype(opcode, self.opc)
                if "optype" in kwargs:
                    assert optype == kwargs.pop("has_args")

                super().__init(
                    opcode,
                    opname,
                    arg,
                    argval,
                    argrepr,
                    offset,
                    starts_line,
                    is_jump_target,
                    positions,
                    optype=optype,
                    has_args=has_args,
                    **kwargs
                )
                self.opc = opc

        self.Instruction = Instruction

    def _print(self, x, file=None):
        if file is None:
            print(x)
        else:
            file.write(str(x) + "\n")

    def code_info(self, x):
        """Formatted details of methods, functions, or code."""
        return _code_info(x, self.python_version_tuple)

    def show_code(self, x, file=None):
        """Print details of methods, functions, or code to *file*.

        If *file* is not provided, the output is printed on stdout.
        """
        return _show_code(x, self.opc.version_tuple, file, is_pypy=self.is_pypy)

    def stack_effect(self, opcode, oparg: int = 0, jump=None):
        """Compute the stack effect of *opcode* with argument *oparg*."""
        return _stack_effect(opcode, self.opc, oparg, jump)

    def pretty_flags(self, flags):
        """Return pretty representation of code flags."""
        return _pretty_flags(flags)

    def dis(self, x=None, file=None):
        """Disassemble classes, methods, functions, generators, or code.

        With no argument, disassemble the last traceback.

        """
        self._print(self.Bytecode(x).dis(), file)

    def distb(self, tb=None, file=None):
        """Disassemble a traceback (default: last traceback)."""
        if tb is None:
            try:
                tb = sys.last_traceback
            except AttributeError:
                raise RuntimeError("no last traceback to disassemble")
            while tb.tb_next:
                tb = tb.tb_next
        self.disassemble(tb.tb_frame.f_code, tb.tb_lasti, file=file)

    def disassemble(self, code, lasti=-1, file=None):
        """Disassemble a code object."""
        return self.disco(code, lasti, file)

    def disco(self, code, lasti=-1, file=None):
        """Disassemble a code object."""
        return _disco(
            self.python_version_tuple,
            code,
            timestamp=None,
            out=file,
            is_pypy=self.is_pypy,
            is_graal=self.is_graal,
        )

    def get_instructions(self, x, first_line=None):
        """Iterator for the opcodes in methods, functions or code

        Generates a series of Instruction named tuples giving the details of
        each operation in the supplied code.

        If *first_line* is not None, it indicates the line number that should
        be reported for the first source line in the disassembled code.
        Otherwise, the source line information (if any) is taken directly from
        the disassembled code object.
        """
        return self.Bytecode(x).get_instructions(x, first_line)

    def findlinestarts(self, code):
        """Find the offsets in a byte code which are start of lines in the source.

        Generate pairs (offset, lineno) as described in Python/compile.c.

        """
        return self.opc.findlinestarts(code)

    def findlabels(self, code):
        """Detect all offsets in a byte code which are jump targets.

        Return the list of offsets.
        """
        return self.opc.findlabels(code, self.opc)


def make_std_api(python_version=sys.version_info, variant=VARIANT):
    """
    Generate an object which can be used in the same way as the Python
    standard ``dis`` module.

    The difference is that the generated 'module' can be
    used to disassemble byte / word code from a different python version than
    the version of the interpreter under which we are running.

    :param python_version: Generate a dis module for this version of python
                           (defaults to the currently running python version.)
    :param variant:        The string denoting the variant of the python version
                           being run, for example 'pypy' or 'alpha0', 'rc1' etc.,
                           or None to auto-detect based on the currently running
                           interpreter.

    :return: An Object which can be used like the std ``dis`` module.
    """
    if isinstance(python_version, float):
        major = int(python_version)
        minor = int(((python_version - major) + 0.05) * 10)
        python_version = (major, minor)
    return _StdApi(python_version, variant)


_std_api = make_std_api()

hasconst = _std_api.hasconst
hasname = _std_api.hasname
opmap = _std_api.opmap
opname = _std_api.opname
EXTENDED_ARG = _std_api.EXTENDED_ARG
HAVE_ARGUMENT = _std_api.HAVE_ARGUMENT
xcode = _std_api.xcode
opc = _std_api.opc
Bytecode = _std_api.Bytecode
Instruction = _std_api.Instruction
code_info = _std_api.code_info
_print = _std_api._print
show_code = _std_api.show_code
pretty_flags = _std_api.pretty_flags
dis = _std_api.dis
distb = _std_api.distb
disassemble = _std_api.disassemble
disco = _std_api.disco
get_instructions = _std_api.get_instructions
findlinestarts = _std_api.findlinestarts
findlabels = _std_api.findlabels
