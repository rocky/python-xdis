# (C) Copyright 2016-2017, 2019-2020 by Rocky Bernstein
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

This is a like Python 3.7's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import(
    def_op,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    init_opdata, nargs_op,
    jrel_op,
    name_op, rm_op,
    update_pj3
    )

from xdis.opcodes.opcode_33 import extended_format_MAKE_FUNCTION
import xdis.opcodes.opcode_36 as opcode_36

version = 3.7
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_36, version)

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
rm_op(l, "STORE_ANNOTATION", 127)

# These have a changed stack effect since 3.6
#          OP NAME            OPCODE POP PUSH
#---------------------------------------------------------------
def_op(l, "WITH_CLEANUP_START",   81,  0,  2)
def_op(l, "WITH_CLEANUP_FINISH",  82,  3,  0)
def_op(l, "END_FINALLY",          88,  6,  0)
def_op(l, "POP_EXCEPT",           89,  3,  0) # Pops last 3 values
jrel_op(l, "SETUP_WITH",         143,  0,  6)
jrel_op(l, "SETUP_ASYNC_WITH",   154,  0,  5)

# These are new since Python 3.7
name_op(l, "LOAD_METHOD", 160, 0, 1)
nargs_op(l, "CALL_METHOD", 161, -2, 1)

format_MAKE_FUNCTION_flags = opcode_36.format_MAKE_FUNCTION_flags
format_value_flags = opcode_36.format_value_flags

opcode_arg_fmt = {
    "BUILD_MAP_UNPACK_WITH_CALL": opcode_36.format_BUILD_MAP_UNPACK_WITH_CALL,
    "CALL_FUNCTION": opcode_36.format_CALL_FUNCTION,
    "CALL_FUNCTION_KW": opcode_36.format_CALL_FUNCTION_KW,
    "CALL_FUNCTION_EX": opcode_36.format_CALL_FUNCTION_EX,
    "CALL_METHOD": opcode_36.format_CALL_FUNCTION,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_flags,
    "FORMAT_VALUE": format_value_flags,
    "EXTENDED_ARG": opcode_36.format_extended_arg36
}

opcode_extended_fmt = {
    "CALL_FUNCTION": opcode_36.extended_format_CALL_FUNCTION,
    "CALL_METHOD": opcode_36.extended_format_CALL_METHOD,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
}

update_pj3(globals(), l)

finalize_opcodes(l)
