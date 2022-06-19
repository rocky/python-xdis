# (C) Copyright 2016-2017, 2020-2021 by Rocky Bernstein
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
CPython 3.5 bytecode opcodes

This is a like Python 3.5's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_CALL_FUNCTION,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj3,
    varargs_op,
)

import xdis.opcodes.opcode_34 as opcode_34
from xdis.opcodes.opcode_33 import (
    extended_format_MAKE_FUNCTION,
    format_MAKE_FUNCTION_default_pos_arg,
)

version = 3.5
version_tuple = (3, 5)
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_34, version_tuple)

# fmt: off
# These are removed since Python 3.5.
# Removals happen before adds since
# some opcodes are reused
rm_op(l, "STORE_MAP",                    54)
rm_op(l, "WITH_CLEANUP",                 81)

# Stack effects are change from 3.4
varargs_op(l, "BUILD_MAP",              105, -1, -1)  # arg is count of kwarg items

# These are new since Python 3.5
#          OP NAME                   OPCODE POP PUSH
#---------------------------------------------------
def_op(l, "BINARY_MATRIX_MULTIPLY",      16,  2,  1)
def_op(l, "INPLACE_MATRIX_MULTIPLY",     17,  2,  1)
def_op(l, "GET_AITER",                   50,  1,  1)
def_op(l, "GET_ANEXT",                   51,  0,  1)
def_op(l, "BEFORE_ASYNC_WITH",           52,  0,  1)
def_op(l, "GET_YIELD_FROM_ITER",         69,  1,  1)
def_op(l, "GET_AWAITABLE",               73,  0,  0)
def_op(l, "WITH_CLEANUP_START",          81,  0,  1)
def_op(l, "WITH_CLEANUP_FINISH",         82,  1,  0)

varargs_op(l, "BUILD_LIST_UNPACK",          149, -1,  1)
varargs_op(l, "BUILD_MAP_UNPACK",           150, -1,  1)
varargs_op(l, "BUILD_MAP_UNPACK_WITH_CALL", 151, -1,  1)
varargs_op(l, "BUILD_TUPLE_UNPACK",         152, -1,  1)
varargs_op(l, "BUILD_SET_UNPACK",           153, -1,  1)

jrel_op(l, "SETUP_ASYNC_WITH",          154,  0,  6)
# fmt: on

update_pj3(globals(), l)


def format_BUILD_MAP_UNPACK_WITH_CALL(oparg):
    """The lowest byte of oparg is the count of mappings, the relative
    position of the corresponding callable f is encoded in the second byte
    of oparg."""
    rel_func_pos, count = divmod(oparg, 256)
    return "%d mappings, function at %d" % (count, count + rel_func_pos)


opcode_arg_fmt = {
    "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_pos_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

finalize_opcodes(l)
