# (C) Copyright 2017, 2019-2021 by Rocky Bernstein
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
CPython 2.7 bytecode opcodes

This is a like Python 2.7's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    compare_op,
    def_op,
    extended_format_ATTR,
    extended_format_CALL_FUNCTION,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_MAKE_FUNCTION_default_argc,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    jabs_op,
    jrel_op,
    name_op,
    rm_op,
    update_pj3,
    varargs_op,
)

import xdis.opcodes.opcode_26 as opcode_26

version = 2.7
version_tuple = (2, 7)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_26, version_tuple)

# fmt: off
# Below are opcode changes since Python 2.6
rm_op(l, "BUILD_MAP",     104)
rm_op(l, "LOAD_ATTR",     105)
rm_op(l, "COMPARE_OP",    106)
rm_op(l, "IMPORT_NAME",   107)
rm_op(l, "IMPORT_FROM",   108)
rm_op(l, "JUMP_IF_FALSE", 111)
rm_op(l, "EXTENDED_ARG",  143)
rm_op(l, "JUMP_IF_TRUE",  112)

# These have changed since 2.6 in stack effects.
#          OP NAME            OPCODE   POP PUSH
#-----------------------------------------------
def_op(l, "END_FINALLY",            88,  3,  0)
jrel_op(l, "SETUP_EXCEPT",         121,  0,  0, conditional=True)  # ""
jrel_op(l, "SETUP_FINALLY" ,       122,  0,  0, conditional=True)  # ""


def_op(l, "LIST_APPEND",            94,  2,  1)  # Calls list.append(TOS[-i], TOS).

# Used to implement list comprehensions.
varargs_op(l, 'BUILD_SET',         104, -1,  1)  # TOS is count of set items
def_op(l,  "BUILD_MAP",            105,  0,  1)  # count is in argument
name_op(l, "LOAD_ATTR",            106,  1,  1)  # Operand is in name list
compare_op(l, "COMPARE_OP", 107)

name_op(l, "IMPORT_NAME",          108, 2,   1)  # Index in name list
name_op(l, "IMPORT_FROM",          109, 0,   1)

jabs_op(l, "JUMP_IF_FALSE_OR_POP", 111)  # Target byte offset from beginning of code
jabs_op(l, "JUMP_IF_TRUE_OR_POP",  112)  # ""
jabs_op(l, "POP_JUMP_IF_FALSE",    114, 2,   1, conditional=True)  # ""
jabs_op(l, "POP_JUMP_IF_TRUE",     115, 2,   1, conditional=True)  # ""
jrel_op(l, "SETUP_WITH",           143, 0,   4)

def_op(l, "EXTENDED_ARG", 145)
def_op(l, "SET_ADD", 146, 1, 0)  # Calls set.add(TOS1[-i], TOS).
# Used to implement set comprehensions.
def_op(l, "MAP_ADD",               147, 3, 1)  # Calls dict.setitem(TOS1[-i], TOS, TOS1)
# Used to implement dict comprehensions.
# fmt: on

update_pj3(globals(), l)

opcode_arg_fmt = {
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,
    "EXTENDED_ARG": format_extended_arg,
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

finalize_opcodes(l)

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
