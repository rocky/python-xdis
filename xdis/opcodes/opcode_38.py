# (C) Copyright 2019-2021, 2023 by Rocky Bernstein
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
CPython 3.8 bytecode opcodes

This is like Python 3.8's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_37 as opcode_37
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    nargs_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_37 import opcode_arg_fmt37, opcode_extended_fmt37

version_tuple = (3, 8)
python_implementation = "CPython"

loc = l = locals()

init_opdata(l, opcode_37, version_tuple)

# fmt: off
# These are removed since 3.7...
rm_op(l, "BREAK_LOOP",     80)
rm_op(l, "CONTINUE_LOOP", 119)
rm_op(l, "SETUP_LOOP",    120)
rm_op(l, "SETUP_EXCEPT",  121)

# These are new/changed since Python 3.7

#          OP NAME            OPCODE POP PUSH
# --------------------------------------------
def_op(l, "ROT_FOUR",          6,      4, 4)  # Opcode number changed from 5 to 6. Why?
def_op(l, "BEGIN_FINALLY",     53,     0, 6)
def_op(l, "END_ASYNC_FOR",     54,     7, 0)  # POP is 0, when not 7
def_op(l, "END_FINALLY",       88,     6, 0)  # POP is 6, when not 1
jrel_op(l, "CALL_FINALLY",    162,     0, 1)
nargs_op(l, "POP_FINALLY",    163,     6, 0)  # PUSH/POP vary

# fmt: on

opcode_arg_fmt = opcode_arg_fmt38 = opcode_arg_fmt37.copy()
opcode_extended_fmt = opcode_extended_fmt38 = opcode_extended_fmt37.copy()

update_pj3(globals(), loc)
finalize_opcodes(l)
