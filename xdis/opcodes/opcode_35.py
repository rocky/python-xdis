# (C) Copyright 2016-2017 by Rocky Bernstein
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
CPython 3.5 bytecode opcodes

This is a like Python 3.5's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, init_opdata, finalize_opcodes,
    format_extended_arg, jrel_op, rm_op, update_pj3)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

import xdis.opcodes.opcode_34 as opcode_34

version = 3.5

l = locals()

init_opdata(l, opcode_34, version)

# These are removed since Python 3.5.
# Removals happen before adds since
# some opcodes are reused
rm_op(l, 'STORE_MAP',                    54)
rm_op(l, 'WITH_CLEANUP',                 81)

# These are new since Python 3.5
#          OP NAME                   OPCODE POP PUSH
#---------------------------------------------------
def_op(l, 'BINARY_MATRIX_MULTIPLY',      16,  2,  1)
def_op(l, 'INPLACE_MATRIX_MULTIPLY',     17,  2,  1)
def_op(l, 'GET_AITER',                   50,  1,  1)
def_op(l, 'GET_ANEXT',                   51,  0,  1)
def_op(l, 'BEFORE_ASYNC_WITH',           52)
def_op(l, 'GET_YIELD_FROM_ITER',         69,  0,  1)
def_op(l, 'GET_AWAITABLE',               73,  0,  0)
def_op(l, 'WITH_CLEANUP_START',          81,  0,  1)
def_op(l, 'WITH_CLEANUP_FINISH',         82, -1,  1)
def_op(l, 'BUILD_LIST_UNPACK',          149, -1,  1)
def_op(l, 'BUILD_MAP_UNPACK',           150, -1,  1)
def_op(l, 'BUILD_MAP_UNPACK_WITH_CALL', 151, -1,  1)
def_op(l, 'BUILD_TUPLE_UNPACK',         152, -1,  1)
def_op(l, 'BUILD_SET_UNPACK',           153, -1,  1)
jrel_op(l, 'SETUP_ASYNC_WITH',          154,  0,  6)

update_pj3(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
