# (C) Copyright 2018-2022 by Rocky Bernstein
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
CPython 1.3 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# This is used from outside this module
from xdis.cross_dis import findlabels

import xdis.opcodes.opcode_14 as opcode_14
from xdis.opcodes.base import (
    def_op,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    rm_op,
    # Although these aren't used here, they are exported
    update_pj2,
)

version = 1.3
version_tuple = (1, 3)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_14, version_tuple)

# 1.3 - 1.4 bytecodes differences
rm_op(l, "BINARY_POWER", 19)
def_op(l, "LOAD_GLOBALS", 84)

update_pj2(globals(), l)

opcode_arg_fmt = {
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

finalize_opcodes(l)

opcode_extended_fmt = {
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
}

findlinestarts = opcode_14.findlinestarts
