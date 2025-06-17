# (C) Copyright 2017, 2020-2021, 2023, 2025 by Rocky Bernstein

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
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_33 as opcode_33
from xdis.opcodes.base import finalize_opcodes, free_op, init_opdata, rm_op, update_pj3
from xdis.opcodes.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

version_tuple = (3, 4)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_33, version_tuple)

# fmt: off
# These are removed since Python 3.3
rm_op(loc, "STORE_LOCALS",       69)

# These are new since Python 3.3
free_op(loc, "LOAD_CLASSDEREF", 148)
# fmt: on

opcode_arg_fmt = opcode_arg_fmt34 = opcode_arg_fmt33.copy()
opcode_extended_fmt = opcode_extended_fmt34 = opcode_extended_fmt33

update_pj3(globals(), loc)
finalize_opcodes(loc)
