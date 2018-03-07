# (C) Copyright 2017 by Rocky Bernstein
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

This is similar to the opcode portion in Python 2.0's dis.py library.
"""

import xdis.opcodes.opcode_21 as opcode_21
from xdis.opcodes.base import (
    init_opdata, finalize_opcodes, format_extended_arg, rm_op, update_pj2)

version = 2.0

l = locals()
init_opdata(l, opcode_21, version)

# 2.1 Bytecodes not in 2.0
rm_op(l, 'CONTINUE_LOOP', 119)
rm_op(l, 'MAKE_CLOSURE',  134)
rm_op(l, 'LOAD_CLOSURE',  135)
rm_op(l, 'LOAD_DEREF',    136)
rm_op(l, 'STORE_DEREF',   137)

update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
