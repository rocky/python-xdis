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
CPython 1.1 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

import xdis.opcodes.opcode_12 as opcode_12

# This is used from outside this module
from xdis.cross_dis import findlabels
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    finalize_opcodes,
    format_extended_arg,
    init_opdata,
    update_pj2,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (1, 1)  # 1.2 is the same
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_12, version_tuple)

# These are used outside of this module
findlinestarts = opcode_12.findlinestarts

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt_base2x.copy()

finalize_opcodes(loc)
update_pj2(globals(), loc)
