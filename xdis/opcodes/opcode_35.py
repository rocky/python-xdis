# (C) Copyright 2016-2017, 2020-2021, 2023 by Rocky Bernstein
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

This is like Python 3.5's opcode.py with some classification
of stack usage and information for formatting instructions.
of stack usage.
"""

from typing import Optional, Tuple

import xdis.opcodes.opcode_34 as opcode_34
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format.extended import extended_format_binary_op, get_arglist
from xdis.opcodes.opcode_34 import opcode_arg_fmt34, opcode_extended_fmt34

version_tuple = (3, 5)
python_implementation = "CPython"


loc = locals()

init_opdata(loc, opcode_34, version_tuple)

# fmt: off
# These are removed since Python 3.5.
# Removals happen before adds since
# some opcodes are reused
rm_op(loc, "STORE_MAP",                    54)
rm_op(loc, "WITH_CLEANUP",                 81)

# Stack effects are change from 3.4
varargs_op(loc, "BUILD_MAP",              105, -1, -1)  # arg is count of kwarg items

# These are new since Python 3.5
#          OP NAME                   OPCODE POP PUSH
#---------------------------------------------------
def_op(loc, "BINARY_MATRIX_MULTIPLY",      16,  2,  1)
def_op(loc, "INPLACE_MATRIX_MULTIPLY",     17,  2,  1)
def_op(loc, "GET_AITER",                   50,  1,  1)
def_op(loc, "GET_ANEXT",                   51,  0,  1)
def_op(loc, "BEFORE_ASYNC_WITH",           52,  0,  1)
def_op(loc, "GET_YIELD_FROM_ITER",         69,  1,  1)
def_op(loc, "GET_AWAITABLE",               73,  0,  0)
def_op(loc, "WITH_CLEANUP_START",          81,  0,  1)
def_op(loc, "WITH_CLEANUP_FINISH",         82,  1,  0)

varargs_op(loc, "BUILD_LIST_UNPACK",          149, -1,  1)
varargs_op(loc, "BUILD_MAP_UNPACK",           150, -1,  1)
varargs_op(loc, "BUILD_MAP_UNPACK_WITH_CALL", 151, -1,  1)
varargs_op(loc, "BUILD_TUPLE_UNPACK",         152, -1,  1)
varargs_op(loc, "BUILD_SET_UNPACK",           153, -1,  1)

jrel_op(loc, "SETUP_ASYNC_WITH",          154,  0,  6)
# fmt: on


def extended_format_BINARY_MATRIX_MULTIPLY(opc, instructions):
    return extended_format_binary_op(opc, instructions, "%s @ %s")


def extended_format_INPLACE_MATRIX_MULTIPLY(opc, instructions):
    return extended_format_binary_op(opc, instructions, "%s @= %s")


def format_BUILD_MAP_UNPACK_WITH_CALL(oparg):
    """The lowest byte of oparg is the count of mappings, the relative
    position of the corresponding callable f is encoded in the second byte
    of oparg."""
    rel_func_pos, count = divmod(oparg, 256)
    return "%d mappings, function at %d" % (count, count + rel_func_pos)


def extended_format_BUILD_MAP_35(opc, instructions: list) -> Tuple[str, Optional[int]]:
    arg_count = instructions[0].argval
    if arg_count == 0:
        # Note: caller generally handles this when the below isn't right.
        return "{}", instructions[0].offset
    arglist, _, i = get_arglist(instructions, 0, 2 * arg_count)
    if arglist is not None:
        assert isinstance(i, int)
        arg_pairs = [
            f"{arglist[i]}:{arglist[i+1]}" for i in range(0, len(arglist) - 1, 2)
        ]
        args_str = ", ".join(arg_pairs)
        return "{" + args_str + "}", instructions[i].start_offset
    return "", None


opcode_arg_fmt = opcode_arg_fmt35 = {
    **opcode_arg_fmt34,
    **{
        "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
    },
}

opcode_extended_fmt = opcode_extended_fmt35 = {
    **opcode_extended_fmt34,
    **{
        "BINARY_MATRIX_MULTIPLY": extended_format_BINARY_MATRIX_MULTIPLY,
        "BUILD_MAP": extended_format_BUILD_MAP_35,
        "INPLACE_MATRIX_MULTIPLY": extended_format_INPLACE_MATRIX_MULTIPLY,
    },
}

update_pj3(globals(), loc)
finalize_opcodes(loc)
