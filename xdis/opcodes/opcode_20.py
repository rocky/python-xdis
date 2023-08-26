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
CPython 2.0 bytecode opcodes

This is similar to (but better than) the opcode portion in Python 2.0's dis.py library.
"""

import xdis.opcodes.opcode_21 as opcode_21
from xdis.opcodes.base import (
    finalize_opcodes,
    init_opdata,
    rm_op,
    update_pj2,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (2, 0)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_21, version_tuple)

# fmt: off
# 2.1 Bytecodes not in 2.0
rm_op(loc, "CONTINUE_LOOP", 119)
rm_op(loc, "MAKE_CLOSURE",  134)
rm_op(loc, "LOAD_CLOSURE",  135)
rm_op(loc, "LOAD_DEREF",    136)
rm_op(loc, "STORE_DEREF",   137)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)

# fmt: on
