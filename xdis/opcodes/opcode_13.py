# (C) Copyright 2018-2023 by Rocky Bernstein
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

import xdis.opcodes.opcode_14 as opcode_14

# This is used from outside this module
from xdis.cross_dis import findlabels  # noqa
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    def_op,
    finalize_opcodes,
    init_opdata,
    rm_op,
    update_pj2,
)
from xdis.opcodes.opcode_1x import opcode_extended_fmt_base1x, update_arg_fmt_base1x

version_tuple = (1, 3)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_14, version_tuple)

# 1.3 - 1.4 bytecodes differences
rm_op(loc, "BINARY_POWER", 19)
def_op(loc, "LOAD_GLOBALS", 84)

opcode_arg_fmt = opcode_arg_fmt13 = update_arg_fmt_base1x.copy()
del opcode_arg_fmt["EXTENDED_ARG"]

opcode_extended_fmt = (
    opcode_extended_fmt13
) = opcode_extended_fmt13 = opcode_extended_fmt_base1x.copy()

findlinestarts = opcode_14.findlinestarts

update_pj2(globals(), loc)
finalize_opcodes(loc)
