# (C) Copyright 2021, 2023-2024 by Rocky Bernstein
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
CPython 3.10 bytecode opcodes

This is like Python 3.10's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_39 as opcode_39
from xdis.cross_dis import findlinestarts  # noqa
from xdis.opcodes.base import def_op, finalize_opcodes, init_opdata, rm_op, update_pj3
from xdis.opcodes.opcode_39 import opcode_arg_fmt39, opcode_extended_fmt39

version_tuple = (3, 10)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_39, version_tuple)

# fmt: off

# These are removed since 3.9...
rm_op(loc,  "RERAISE",                  48)

# These are added since 3.9...
#         OP NAME                   OPCODE  POP PUSH
#------------------------------------------------
def_op(loc, "GET_LEN",                  30,   0, 1)
def_op(loc, "MATCH_MAPPING",            31,   0, 1)
def_op(loc, "MATCH_SEQUENCE",           32,   0, 1)
def_op(loc, "MATCH_KEYS",               33,   0, 2)
def_op(loc, "COPY_DICT_WITHOUT_KEYS",   34,   2, 2)
def_op(loc, "ROT_N",                    99,   0, 0)
def_op(loc, "RERAISE",                 119,   3, 0)
def_op(loc, "GEN_START",               129,   1, 0)
def_op(loc, "MATCH_CLASS",             152,   2, 1)

# fmt: on
opcode_arg_fmt = opcode_arg_fmt310 = opcode_arg_fmt39.copy()
opcode_extended_fmt = opcode_extended_fmt310 = opcode_extended_fmt39.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
