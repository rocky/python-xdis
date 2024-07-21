# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
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
CPython 2.6 bytecode opcodes

This is a like Python 2.6's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
"""

import xdis.opcodes.opcode_25 as opcode_25
from xdis.opcodes.base import (
    finalize_opcodes,
    init_opdata,
    name_op,
    rm_op,
    store_op,
    update_pj2,
)
from xdis.opcodes.opcode_2x import opcode_extended_fmt_base2x, update_arg_fmt_base2x

python_implementation = "CPython"

version_tuple = (2, 6)

loc = locals()
init_opdata(loc, opcode_25, version_tuple)

# Below are opcode changes since Python 2.5

# fmt: off
#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
store_op(loc, "STORE_MAP",          54,  3,  1)
rm_op(loc,    "IMPORT_NAME",       107)
name_op(loc,  "IMPORT_NAME",       107,  2,  1)  # Imports namei; TOS and TOS1 provide
                                                 # fromlist and level. Module pushed.
loc["nullaryloadop"].add(107)

# fmt: on

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

# FIXME remove (fix uncompyle6)
update_pj2(globals(), loc)
finalize_opcodes(loc)
