# (C) Copyright 2017, 2020-2021, 2023, 2025 by Rocky Bernstein
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
CPython 2.4 bytecode opcodes

This is a like Python 2.3's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
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

findlabels = xdis.cross_dis.findlabels
python_implementation = cpython_implementation
version_tuple = (2, 4)

loc = locals()
init_opdata(loc, opcode_2x, version_tuple)

# fmt: off
# Bytecodes added since 2.3
#          OP NAME            OPCODE POP PUSH
 # Used to implement list comprehensions.
def_op(loc, 'YIELD_VALUE',          86,  1,  1)
# --------------------------------------------
def_op(loc, "NOP", 9, 0, 0)
def_op(loc, "LIST_APPEND", 18, 2, 0)  # Calls list.append(TOS[-i], TOS).
# Used to implement list comprehensions.
def_op(loc, "YIELD_VALUE", 86, 1, 1)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

# FIXME remove (fix uncompyle6)
update_pj2(globals(), loc)
finalize_opcodes(loc)

# fmt: on
