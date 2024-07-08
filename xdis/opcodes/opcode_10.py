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
CPython 1.0 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

import xdis.opcodes.opcode_11 as opcode_11

# This is used from outside this module
from xdis.cross_dis import findlabels  # noqa
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    finalize_opcodes,
    init_opdata,
    name_op,
    rm_op,
    update_pj2,
)
from xdis.opcodes.opcode_11 import opcode_arg_fmt11, opcode_extended_fmt11

version_tuple = (1, 0)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_11, version_tuple)

# fmt: off
# 1.0 - 1.1 bytecodes differences
rm_op(loc,  "LOAD_GLOBALS", 84)
rm_op(loc,  "LOAD_FAST",         124)
name_op(loc, "LOAD_FAST",        124, 0, 1)  # Local variable number
loc["nullaryloadop"].add(124)

# fmt: on

findlinestarts = opcode_11.findlinestarts

opcode_arg_fmt = opcode_arg_fmt11.copy()
opcode_extended_fmt = opcode_extended_fmt11.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
