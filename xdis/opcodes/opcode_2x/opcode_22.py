# (C) Copyright 2017, 2019, 2021, 2023, 2025 by Rocky Bernstein
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
CPython 2.2 bytecode opcodes

This is similar to the opcode portion in Python 2.2's dis.py library.
"""

import xdis.cross_dis
from xdis.opcodes.base import (  # noqa
    cpython_implementation,
    def_op,
    finalize_opcodes,
    init_opdata,
    update_pj2,
)
from xdis.opcodes.opcode_2x.opcode_2x import (
    opcode_extended_fmt_base2x,
    update_arg_fmt_base2x,
)

from . import opcode_2x

version_tuple = (2, 2)
python_implementation = cpython_implementation
findlabels = xdis.cross_dis.findlabels

loc = locals()
init_opdata(loc, opcode_2x, version_tuple)

# 2.2 Bytecodes not in 2.3
def_op(loc, "FOR_LOOP", 114)
def_op(loc, "SET_LINENO", 127, 0, 0)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
