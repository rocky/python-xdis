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
CPython 1.6 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# This is used from outside this module
from xdis.cross_dis import findlabels, findlinestarts  # noqa

import xdis.opcodes.opcode_15 as opcode_15
from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RETURN_VALUE,
    init_opdata,
    nargs_op,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_MAKE_FUNCTION_default_argc,
    format_extended_arg,
    update_pj2,
)

version = 1.6
version_tuple = (1, 6)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_15, version_tuple)

# fmt: off
# 1.6 Bytecodes not in 1.5
nargs_op(l, "CALL_FUNCTION_VAR",    140, -1, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_KW",     141, -1, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_VAR_KW", 142, -1, 1)  # #args + (#kwargs << 8)

update_pj2(globals(), l)

opcode_arg_fmt = {"EXTENDED_ARG": format_extended_arg}

opcode_arg_fmt = {
    "EXTENDED_ARG":         format_extended_arg,
    "CALL_FUNCTION":        format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW":     format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "MAKE_FUNCTION":        format_MAKE_FUNCTION_default_argc,
}

opcode_extended_fmt = {
    "LOAD_ATTR":     extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RETURN_VALUE":  extended_format_RETURN_VALUE,
    "STORE_ATTR":    extended_format_ATTR,
}
# fmt: on

finalize_opcodes(l)
