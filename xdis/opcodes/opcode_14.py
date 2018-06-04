# (C) Copyright 2018 by Rocky Bernstein
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
CPython 1.4 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# This is used from outside this module
from xdis.bytecode import findlabels

import xdis.opcodes.opcode_15 as opcode_15
from xdis.opcodes.base import (
    init_opdata,
    def_op, name_op, rm_op, varargs_op,
    finalize_opcodes, format_extended_arg,
    # Although these aren't used here, they are exported
    update_pj2
    )

version = 1.4

l = locals()
init_opdata(l, opcode_15, version)

# 1.4 Bytecodes not in 1.5
def_op(l, 'UNARY_CALL',         14)
def_op(l, 'BINARY_CALL',        26)
def_op(l, 'RAISE_EXCEPTION',    81)
def_op(l, 'BUILD_FUNCTION',     86)
varargs_op(l, 'UNPACK_ARG',     94)   # Number of arguments expected
varargs_op(l, 'UNPACK_VARARG',  99)  # Minimal number of arguments
name_op(l, 'LOAD_LOCAL',       115)
varargs_op(l, 'SET_FUNC_ARGS', 117)  # Argcount
varargs_op(l, 'RESERVE_FAST',  123)  # Number of local variables

update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)

def findlinestarts(co, dup_lines=False):
    code = co.co_code
    n = len(code)
    offset = 0
    while offset < n:
        op = code[offset]
        offset += 1
        if op == l['opmap']['SET_LINENO'] and offset > 0:
            lineno = code[offset] + code[offset+1]*256
            yield (offset-1, lineno)
            pass
        if op >= l['HAVE_ARGUMENT']:
            offset += 2
            pass
        pass
