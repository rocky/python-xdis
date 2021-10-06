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
CPython 2.0 bytecode opcodes

This is similar to (but better than) the opcode portion in Python 2.0's dis.py library.
"""

import xdis.opcodes.opcode_21 as opcode_21
from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_MAKE_FUNCTION_default_argc,
    format_extended_arg,
    init_opdata,
    rm_op,
    update_pj2,
)

version = 2.0
version_tuple = (2, 0)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_21, version_tuple)

# fmt: off
# 2.1 Bytecodes not in 2.0
rm_op(l, "CONTINUE_LOOP", 119)
rm_op(l, "MAKE_CLOSURE",  134)
rm_op(l, "LOAD_CLOSURE",  135)
rm_op(l, "LOAD_DEREF",    136)
rm_op(l, "STORE_DEREF",   137)

update_pj2(globals(), l)

finalize_opcodes(l)

opcode_arg_fmt = {
    "CALL_FUNCTION":        format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW":     format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG":         format_extended_arg,
    "MAKE_FUNCTION":        format_MAKE_FUNCTION_default_argc,
}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION":        extended_format_MAKE_FUNCTION_older,
    "RETURN_VALUE":         extended_format_RETURN_VALUE,
    "STORE_ATTR":           extended_format_ATTR,
}
# fmt: on
