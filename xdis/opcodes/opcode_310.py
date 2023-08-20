# (C) Copyright 2021, 2023 by Rocky Bernstein
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
CPython 3.10 bytecode opcodes

This is a like Python 3.10's opcode.py
"""

import xdis.opcodes.opcode_39 as opcode_39
from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_BINARY_ADD,
    extended_format_BINARY_FLOOR_DIVIDE,
    extended_format_BINARY_MODULO,
    extended_format_BINARY_SUBSCR,
    extended_format_BINARY_SUBTRACT,
    extended_format_COMPARE_OP,
    extended_format_INPLACE_ADD,
    extended_format_INPLACE_FLOOR_DIVIDE,
    extended_format_INPLACE_SUBTRACT,
    extended_format_INPLACE_TRUE_DIVIDE,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    init_opdata,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_36 import (
    extended_format_CALL_FUNCTION,
    extended_format_CALL_METHOD,
    extended_format_MAKE_FUNCTION,
    format_BUILD_MAP_UNPACK_WITH_CALL,
    format_CALL_FUNCTION_EX,
    format_CALL_FUNCTION_KW,
    format_extended_arg36,
    format_MAKE_FUNCTION,
)
from xdis.opcodes.opcode_37 import extended_format_RAISE_VARARGS, format_RAISE_VARARGS

version_tuple = (3, 10)
python_implementation = "CPython"

loc = l = locals()

init_opdata(l, opcode_39, version_tuple)

# fmt: off
format_value_flags = opcode_39.format_value_flags
# These are removed since 3.9...
rm_op(l,  "RERAISE",                  48)

# These are added since 3.9...
#         OP NAME                 OPCODE  POP PUSH
#------------------------------------------------
def_op(l, "GET_LEN",                  30,   0, 1)
def_op(l, "MATCH_MAPPING",            31,   0, 1)
def_op(l, "MATCH_SEQUENCE",           32,   0, 1)
def_op(l, "MATCH_KEYS",               33,   0, 2)
def_op(l, "COPY_DICT_WITHOUT_KEYS",   34,   2, 2)
def_op(l, "ROT_N",                    99,   0, 0)
def_op(l, "RERAISE",                 119,   3, 0)
def_op(l, "GEN_START",               129,   1, 0)
def_op(l, "MATCH_CLASS",             152,   2, 1)
# fmt: on


def format_extended_is_op(arg):
    return "is" if arg == 0 else "is not"


def format_extended_contains_op(arg):
    return "in" if arg == 0 else "not in"


opcode_arg_fmt = {
    "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
    "CALL_FUNCTION_EX": format_CALL_FUNCTION_EX,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_KW,
    "CONTAINS_OP": format_extended_contains_op,
    "EXTENDED_ARG": format_extended_arg36,
    "FORMAT_VALUE": format_value_flags,
    "IS_OP": format_extended_is_op,
    "MAKE_FUNCTION": format_MAKE_FUNCTION,
    "RAISE_VARARGS": format_RAISE_VARARGS,
}

opcode_extended_fmt = {
    "BINARY_ADD": extended_format_BINARY_ADD,
    "BINARY_FLOOR_DIVIDE": extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO": extended_format_BINARY_MODULO,
    "BINARY_SUBSCR": extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT": extended_format_BINARY_SUBTRACT,
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "CALL_METHOD": extended_format_CALL_METHOD,
    "COMPARE_OP": extended_format_COMPARE_OP,
    "INPLACE_ADD": extended_format_INPLACE_ADD,
    "INPLACE_FLOOR_DIVIDE": extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_SUBTRACT": extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE": extended_format_INPLACE_TRUE_DIVIDE,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
# fmt: on

update_pj3(globals(), l)

finalize_opcodes(l)
