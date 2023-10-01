# (C) Copyright 2017, 2019-2021, 2023 by Rocky Bernstein
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
CPython 1.5 bytecode opcodes

This is a like Python 1.5's opcode.py with some classification
of stack usage and information for formatting instructions.
of stack usage.
"""

import xdis.opcodes.opcode_1x as opcode_1x
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    finalize_opcodes,
    init_opdata,
    update_pj2,
)
from xdis.opcodes.opcode_1x import opcode_extended_fmt_base1x, update_arg_fmt_base1x

version_tuple = (1, 5)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_1x, version_tuple)

# opcode_1x is based on 1.5 so there are no opcodes to add or change.
# If there were, they'd be listed below.

opcode_arg_fmt = update_arg_fmt_base1x.copy()
opcode_extended_fmt = opcode_extended_fmt_base1x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
