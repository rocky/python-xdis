# (C) Copyright 2017, 2020-2021 by Rocky Bernstein
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
CPython 2.6 bytecode opcodes

This is a like Python 2.6's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
"""

from xdis.opcodes.base import (
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
    name_op,
    rm_op,
    store_op,
    update_pj2,
)
import xdis.opcodes.opcode_25 as opcode_25

python_implementation = "CPython"

version = 2.6
version_tuple = (2, 6)

l = locals()
init_opdata(l, opcode_25, version_tuple)

# Below are opcode changes since Python 2.5

# fmt: off
#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
store_op(l, "STORE_MAP",          54,  3,  1)
rm_op(l,    "IMPORT_NAME",       107)
name_op(l,  "IMPORT_NAME",       107,  2,  1)  # Imports namei; TOS and TOS1 provide fromlist and level. Module pushed.
# fmt: on

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
finalize_opcodes(l)
