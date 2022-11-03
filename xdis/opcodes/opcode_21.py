# (C) Copyright 2017, 2019 by Rocky Bernstein
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
CPython 2.1 bytecode opcodes

This is similar to the opcode portion in Python 2.1's dis.py library.
"""

import xdis.opcodes.opcode_22 as opcode_22
from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_extended_arg,
    init_opdata,
    rm_op,
    update_pj2,
)

version = 2.1
version_tuple = (2, 1)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_22, version_tuple)

# 2.1 bytecodes changes from 2.2
rm_op(l, "BINARY_FLOOR_DIVIDE", 26)
rm_op(l, "BINARY_TRUE_DIVIDE", 27)
rm_op(l, "INPLACE_FLOOR_DIVIDE", 28)
rm_op(l, "INPLACE_TRUE_DIVIDE", 29)
rm_op(l, "GET_ITER", 68)
rm_op(l, "YIELD_VALUE", 86)
rm_op(l, "FOR_ITER", 93)

update_pj2(globals(), l)

finalize_opcodes(l)

opcode_arg_fmt = {"EXTENDED_ARG": format_extended_arg}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
