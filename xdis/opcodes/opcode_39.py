# (C) Copyright 2019-2021, 2023 by Rocky Bernstein
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

This is a like Python 3.9's opcode.py
"""

import xdis.opcodes.opcode_38 as opcode_38
from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_BINARY_ADD,
    extended_format_BINARY_FLOOR_DIVIDE,
    extended_format_BINARY_MODULO,
    extended_format_BINARY_SUBSCR,
    extended_format_BINARY_SUBTRACT,
    extended_format_BINARY_TRUE_DIVIDE,
    extended_format_COMPARE_OP,
    extended_format_INPLACE_ADD,
    extended_format_INPLACE_FLOOR_DIVIDE,
    extended_format_INPLACE_SUBTRACT,
    extended_format_INPLACE_TRUE_DIVIDE,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    init_opdata,
    jabs_op,
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
def_op(loc, 'RERAISE',                 48,   3, 0)
def_op(loc, 'WITH_EXCEPT_START',       49,   0, 1)
def_op(loc, 'LOAD_ASSERTION_ERROR',    74,   0, 1)
def_op(loc, 'LIST_TO_TUPLE',           82,   1, 1)

def_op(loc, 'IS_OP',                  117,   2, 1)
jabs_op(loc, 'JUMP_IF_NOT_EXC_MATCH', 121,   2, 0)
def_op(loc, 'CONTAINS_OP',            118,   2, 1)
def_op(loc, 'LIST_EXTEND',            162,   2, 1)
def_op(loc, 'SET_UPDATE',             163,   2, 1)
def_op(loc, 'DICT_MERGE',             164,   2, 1)
def_op(loc, 'DICT_UPDATE',            165,   2, 1)

format_value_flags = opcode_38.format_value_flags


def format_extended_is_op(arg):
    return "is" if arg == 0 else "is not"


def format_extended_contains_op(arg):
    return "in" if arg == 0 else "not in"


opcode_arg_fmt = {
    "BUILD_MAP_UNPACK_WITH_CALL": format_BUILD_MAP_UNPACK_WITH_CALL,
    "CALL_FUNCTION_EX": format_CALL_FUNCTION_EX,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_KW,
    "CONTAINS_OP":      format_extended_contains_op,
    "EXTENDED_ARG":     format_extended_arg36,
    "FORMAT_VALUE":     format_value_flags,
    "IS_OP":            format_extended_is_op,
    "MAKE_FUNCTION":    format_MAKE_FUNCTION,
    "RAISE_VARARGS":    format_RAISE_VARARGS,
}

opcode_extended_fmt = {
    "BINARY_ADD":            extended_format_BINARY_ADD,
    "BINARY_FLOOR_DIVIDE":   extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO":         extended_format_BINARY_MODULO,
    "BINARY_SUBSCR":         extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT":       extended_format_BINARY_SUBTRACT,
    "BINARY_TRUE_DIVIDE":    extended_format_BINARY_TRUE_DIVIDE,
    "CALL_FUNCTION":         extended_format_CALL_FUNCTION,
    "CALL_METHOD":           extended_format_CALL_METHOD,
    "COMPARE_OP":            extended_format_COMPARE_OP,
    "INPLACE_ADD":           extended_format_INPLACE_ADD,
    "INPLACE_FLOOR_DIVIDE":  extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_SUBTRACT":      extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE":   extended_format_INPLACE_TRUE_DIVIDE,
    "LOAD_ATTR":             extended_format_ATTR,
    "MAKE_FUNCTION":         extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS":         extended_format_RAISE_VARARGS,
    "RETURN_VALUE":          extended_format_RETURN_VALUE,
    "STORE_ATTR":            extended_format_ATTR,
}
# fmt: on

update_pj3(globals(), loc)

finalize_opcodes(loc)
