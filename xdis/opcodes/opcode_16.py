# (C) Copyright 2019-2021, 2023-2024 by Rocky Bernstein
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

import xdis.opcodes.opcode_15 as opcode_15

# This is used from outside this module
from xdis.cross_dis import findlabels, findlinestarts  # noqa
from xdis.opcodes.base import call_op, finalize_opcodes, init_opdata, update_pj2
from xdis.opcodes.opcode_2x import opcode_extended_fmt_base2x, update_arg_fmt_base2x

version_tuple = (1, 6)
python_implementation = "CPython"

loc = locals()

# These are just to silence the import above
loc["findlindstarts"] = findlinestarts
loc["findlabels"] = findlabels

init_opdata(loc, opcode_15, version_tuple)

# fmt: off
# 1.6 Bytecodes not in 1.5
call_op(loc, "CALL_FUNCTION_VAR",    140, -1, 1)  # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_KW",     141, -1, 1)  # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_VAR_KW", 142, -1, 1)  # #args + (#kwargs << 8)

# fmt: on

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
