# (C) Copyright 2019-2021 by Rocky Bernstein
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

from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
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
)

from xdis.opcodes.opcode_36 import format_MAKE_FUNCTION_flags
from xdis.opcodes.opcode_37 import extended_format_RAISE_VARARGS, format_RAISE_VARARGS
import xdis.opcodes.opcode_38 as opcode_38

version = 3.9
version_tuple = (3, 9)
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_38, version_tuple)

# fmt: off
# These are removed since 3.8...
rm_op(l, "BEGIN_FINALLY",       53)
rm_op(l, "WITH_CLEANUP_START",  81)
rm_op(l, "WITH_CLEANUP_FINISH", 82)
rm_op(l, "END_FINALLY",         88)
rm_op(l, "BUILD_LIST_UNPACK",  149)
rm_op(l, "BUILD_MAP_UNPACK",   150)
rm_op(l, "BUILD_MAP_UNPACK_WITH_CALL", 151)
rm_op(l, "BUILD_TUPLE_UNPACK", 152)
rm_op(l, "BUILD_SET_UNPACK",   153)
rm_op(l, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(l, "CALL_FINALLY",       162)
rm_op(l, "POP_FINALLY",        163)


# These are new since Python 3.9

#          OP NAME               OPCODE  POP PUSH
#------------------------------------------------
def_op(l, 'RERAISE',                 48,   3, 0)
def_op(l, 'WITH_EXCEPT_START',       49,   0, 1)
def_op(l, 'LOAD_ASSERTION_ERROR',    74,   0, 1)
def_op(l, 'LIST_TO_TUPLE',           82,   1, 1)

def_op(l, 'IS_OP',                  117,   2, 1)
jabs_op(l, 'JUMP_IF_NOT_EXC_MATCH', 121,   2, 0)
def_op(l, 'CONTAINS_OP',            118,   2, 1)
def_op(l, 'LIST_EXTEND',            162,   2, 1)
def_op(l, 'SET_UPDATE',             163,   2, 1)
def_op(l, 'DICT_MERGE',             164,   2, 1)
def_op(l, 'DICT_UPDATE',            165,   2, 1)

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
    "MAKE_FUNCTION":    format_MAKE_FUNCTION_flags,
    "RAISE_VARARGS":    format_RAISE_VARARGS,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "CALL_METHOD":   extended_format_CALL_METHOD,
    "LOAD_ATTR":     extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS,
    "RETURN_VALUE":  extended_format_RETURN_VALUE,
    "STORE_ATTR":    extended_format_ATTR,
}
# fmt: on

update_pj3(globals(), l)

finalize_opcodes(l)
