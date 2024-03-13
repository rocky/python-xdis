# (C) Copyright 2016-2017, 2019-2021, 2023-2024
# by Rocky Bernstein
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
CPython 3.7 bytecode opcodes

This is like Python 3.7's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

from copy import copy

import xdis.opcodes.opcode_36 as opcode_36
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_36 import opcode_arg_fmt36, opcode_extended_fmt36

version_tuple = (3, 7)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_36, version_tuple)

### Opcodes that have changed drastically ####


# BUILD_MAP_UNPACK_WITH_CALL oparg

# oparg is the number of unpacked mappings which no longer limited by
# 255. As in BUILD_MAP_UNPACK.The location of the function is `oparg +
# 2`.


# CALL_FUNCTION oparg

# oparg is the number of positional arguments on the stack which no
# longer limited by 255.


# CALL_FUNCTION_KW oparg

# This is a different opcode from before, with the name of a similar
# opcode as before. It s like CALL_FUNCTION but values of keyword
# arguments are pushed on the stack after values of positional
# arguments, and then a constant tuple of keyword names is pushed on
# the top of the stack.  *oparg* is the sum of numbers of positional
# and keyword arguments.  The number of keyword arguments is
# determined by the length of the tuple of keyword names.

# CALL_FUNCTION_EX** takes 2 to 3 arguments on the stack: the
# function, the tuple of positional arguments, and optionally the dict
# of keyword arguments if bit 0 of *oparg* is 1.


# MAKE_FUNCTION oparg

# This is a different opcode from before.

# The tuple of default values for positional-or-keyword parameters,
# the dict of default values for keyword-only parameters, the dict of
# annotations and the closure are pushed on the stack if corresponding
# bit (0-3) is set. They are followed by the code object and the
# qualified name of the function.

# These are removed since 3.6...
# and STORE_ANNOTATION introduced in 3.6!
rm_op(loc, "STORE_ANNOTATION", 127)

# fmt: off
# These have a changed stack effect since 3.6
#          OP NAME            OPCODE POP PUSH
#---------------------------------------------------------------
def_op(loc, "WITH_CLEANUP_START",   81,  0,  2)
def_op(loc, "WITH_CLEANUP_FINISH",  82,  3,  0)
def_op(loc, "END_FINALLY",          88,  6,  0)
def_op(loc, "POP_EXCEPT",           89,  3,  0) # Pops last 3 values
jrel_op(loc, "SETUP_WITH",         143,  0,  6)
jrel_op(loc, "SETUP_ASYNC_WITH",   154,  0,  5)

# These are new since Python 3.7
name_op(loc, "LOAD_METHOD",        160,  0,  1)
nargs_op(loc, "CALL_METHOD",       161, -2,  1)

format_MAKE_FUNCTION = opcode_36.format_MAKE_FUNCTION
format_value_flags = opcode_36.format_value_flags

def extended_format_RAISE_VARARGS(opc, instructions):
    raise_inst = instructions[0]
    assert raise_inst.opname == "RAISE_VARARGS"
    argc = raise_inst.argval
    start_offset = raise_inst.start_offset
    if argc == 0:
        return "reraise", start_offset
    elif argc == 1:
        exception_name_inst = instructions[1]
        start_offset = exception_name_inst.start_offset
        if exception_name_inst.tos_str:
            exception_name = exception_name_inst.tos_str
        else:
            exception_name = exception_name_inst.argrepr
        if exception_name is not None:
            return "raise %s()" % exception_name, start_offset
    return format_RAISE_VARARGS(raise_inst.argval), start_offset

def format_RAISE_VARARGS(argc):
    assert 0 <= argc <= 2
    if argc == 0:
        return "reraise"
    elif argc == 1:
        return "exception instance"
    elif argc == 2:
        return "exception instance with __cause__"

opcode_arg_fmt = opcode_arg_fmt37 = copy(opcode_arg_fmt36)
opcode_arg_fmt.update(
    {"RAISE_VARARGS": format_RAISE_VARARGS}
)

opcode_extended_fmt = opcode_extended_fmt37 = copy(opcode_extended_fmt36)
opcode_extended_fmt.update({
     "RAISE_VARARGS": extended_format_RAISE_VARARGS,
    }
)

update_pj3(globals(), loc)
finalize_opcodes(loc)
