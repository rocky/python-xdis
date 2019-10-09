# (C) Copyright 2019 by Rocky Bernstein
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
CPython 1.1 and 1.2 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# This is used from outside this module
from xdis.bytecode import findlabels

import xdis.opcodes.opcode_13 as opcode_13
from xdis.opcodes.base import (
    init_opdata,
    finalize_opcodes,
    format_extended_arg,
    # Although these aren't used here, they are exported
    update_pj2,
)

version = 1.1 # 1.2 is the same

l = locals()
init_opdata(l, opcode_13, version)

update_pj2(globals(), l)

opcode_arg_fmt = {"EXTENDED_ARG": format_extended_arg}

finalize_opcodes(l)

findlinestarts = opcode_13.findlinestarts
