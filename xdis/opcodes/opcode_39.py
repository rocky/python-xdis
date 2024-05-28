# (C) Copyright 2019-2021, 2023-2024 by Rocky Bernstein
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
CPython 3.9 bytecode opcodes

This is like Python 3.9's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

from typing import Optional, Tuple

import xdis.opcodes.opcode_38 as opcode_38
from xdis.opcodes.base import (
    binary_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jabs_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_38 import opcode_arg_fmt38, opcode_extended_fmt38

version_tuple = (3, 9)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_38, version_tuple)

# fmt: off
# These are removed since 3.8...
rm_op(loc, "BEGIN_FINALLY",       53)
rm_op(loc, "WITH_CLEANUP_START",  81)
rm_op(loc, "WITH_CLEANUP_FINISH", 82)
rm_op(loc, "END_FINALLY",         88)
rm_op(loc, "BUILD_LIST_UNPACK",  149)
rm_op(loc, "BUILD_MAP_UNPACK",   150)
rm_op(loc, "BUILD_MAP_UNPACK_WITH_CALL", 151)
rm_op(loc, "BUILD_TUPLE_UNPACK", 152)
rm_op(loc, "BUILD_SET_UNPACK",   153)
rm_op(loc, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(loc, "CALL_FINALLY",       162)
rm_op(loc, "POP_FINALLY",        163)


# These are new since Python 3.9

#          OP NAME               OPCODE  POP PUSH
#------------------------------------------------
def_op(loc, "RERAISE",                 48,   3, 0)
def_op(loc, "WITH_EXCEPT_START",       49,   0, 1)
def_op(loc, "LOAD_ASSERTION_ERROR",    74,   0, 1)
def_op(loc, "LIST_TO_TUPLE",           82,   1, 1)

binary_op(loc, "IS_OP",               117)
jabs_op(loc, "JUMP_IF_NOT_EXC_MATCH", 121,   2, 0)
binary_op(loc, "CONTAINS_OP",         118,   2, 1)
def_op(loc, "LIST_EXTEND",            162,   2, 1)
def_op(loc, "SET_UPDATE",             163,   2, 1)
def_op(loc, "DICT_MERGE",             164,   2, 1)
def_op(loc, "DICT_UPDATE",            165,   2, 1)

# fmt: on


def extended_format_CONTAINS_OP(
    opc, instructions
) -> Tuple[Optional[str], Optional[int]]:
    instr = instructions[0]
    return extended_format_binary_op(
        opc, instructions, f"%s {format_CONTAINS_OP(instr.arg)} %s"
    )


def extended_format_IS_OP(opc, instructions) -> Tuple[Optional[str], Optional[int]]:
    instr = instructions[0]
    return extended_format_binary_op(
        opc, instructions, f"%s {format_IS_OP(instr.arg)} %s"
    )


def format_CONTAINS_OP(arg):
    return "in" if arg == 0 else "not in"


def format_IS_OP(arg):
    return "is" if arg == 0 else "is not"


opcode_arg_fmt = opcode_arg_fmt39 = {
    **opcode_arg_fmt38,
    **{
        "CONTAINS_OP": format_CONTAINS_OP,
        "IS_OP": format_IS_OP,
    },
}

opcode_extended_fmt = opcode_extended_fmt39 = {
    **opcode_extended_fmt38.copy(),
    **{
        "CONTAINS_OP": extended_format_CONTAINS_OP,
        "IS_OP": extended_format_IS_OP,
    },
}

update_pj3(globals(), loc)
finalize_opcodes(loc)
