# (C) Copyright 2019-2023 by Rocky Bernstein
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
CPython 1.2 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

import xdis.opcodes.opcode_13 as opcode_13

# This is used from outside this module
from xdis.cross_dis import findlabels  # noqa
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    finalize_opcodes,
    init_opdata,
    name_op,
    rm_op,
    store_op,
    update_pj2,
)
from xdis.opcodes.opcode_13 import opcode_arg_fmt13, opcode_extended_fmt13

version_tuple = (1, 2)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_13, version_tuple)

# fmt: off
# 1.3 - 1.2 bytecodes differences
rm_op(loc,  "LOAD_FAST",         124)
rm_op(loc,  "STORE_FAST",        125)

name_op(loc, "LOAD_FAST",        124, 0, 1)  # Local variable number
loc["nullaryloadop"].add(124)

store_op(loc, "STORE_FAST",      125, 1, 0, is_type="name")  # Local variable number

# fmt: on

# These are used outside of this module
findlinestarts = opcode_13.findlinestarts

opcode_arg_fmt = opcode_arg_fmt12 = opcode_arg_fmt13.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt13.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
