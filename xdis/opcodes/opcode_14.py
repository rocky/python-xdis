# (C) Copyright 2018-2021, 2023 by Rocky Bernstein
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

import xdis.opcodes.opcode_15 as opcode_15

# This is used from outside this module
from xdis.cross_dis import findlabels  # noqa
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    def_op,
    finalize_opcodes,
    init_opdata,
    name_op,
    update_pj2,
    varargs_op,
)
from xdis.opcodes.opcode_1x import opcode_extended_fmt_base1x, update_arg_fmt_base1x

version_tuple = (1, 4)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_15, version_tuple)

# fmt: off
# 1.4 Bytecodes not in 1.5

def_op(loc, "UNARY_CALL",         14)
def_op(loc, "BINARY_CALL",        26)
def_op(loc, "RAISE_EXCEPTION",    81)
def_op(loc, "BUILD_FUNCTION",     86)
varargs_op(loc, "UNPACK_ARG",     94)  # Number of arguments expected
varargs_op(loc, "UNPACK_VARARG",  99)  # Minimal number of arguments
name_op(loc, "LOAD_LOCAL",       115)
loc["nullaryloadop"].add(115)

varargs_op(loc, "SET_FUNC_ARGS", 117)  # Argcount
varargs_op(loc, "RESERVE_FAST",  123)  # Number of local variables
# fmt: on


def findlinestarts(co, dup_lines=False):
    code = co.co_code
    n = len(code)
    offset = 0
    while offset < n:
        op = code[offset]
        offset += 1
        if op == loc["opmap"]["SET_LINENO"] and offset > 0:
            lineno = code[offset] + code[offset + 1] * 256
            yield (offset + 2, lineno)
            pass
        if op >= loc["HAVE_ARGUMENT"]:
            offset += 2
            pass
        pass


opcode_arg_fmt = update_arg_fmt_base1x.copy()
opcode_extended_fmt = opcode_extended_fmt_base1x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
