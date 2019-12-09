# (C) Copyright 2019 by Rocky Bernstein
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

This is a like Python 3.9's opcode.py
"""

from xdis.opcodes.base import(
    const_op,
    def_op,
    finalize_opcodes,
    format_extended_arg36,
    init_opdata,
    update_pj3
    )

import xdis.opcodes.opcode_38 as opcode_38

version = 3.9

l = locals()

init_opdata(l, opcode_38, version)

# These are new since Python 3.9

#          OP NAME              OPCODE  POP PUSH
#-----------------------------------------------
def_op(l, 'RERAISE',                48,   0, 0)
const_op(l, 'LOAD_ASSERTION_ERROR', 74,   0, 1)

format_MAKE_FUNCTION_arg = opcode_38.format_MAKE_FUNCTION_arg
format_value_flags = opcode_38.format_value_flags

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'FORMAT_VALUE': format_value_flags,
    'EXTENDED_ARG': format_extended_arg36
}

update_pj3(globals(), l)

finalize_opcodes(l)
