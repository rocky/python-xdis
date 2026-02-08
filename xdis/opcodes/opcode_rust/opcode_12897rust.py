# (C) Copyright 2025 by Rocky Bernstein
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
RustPython 3.12.0 bytecode opcodes for version 0.40. There are other Rust 3.12 with different opcodes!
"""

#FIXME: this needs a lot of going over.

from typing import Dict, List, Optional, Tuple

import xdis.opcodes.opcode_3x.opcode_311 as opcode_311

# import xdis.opcodes.opcode_313 as opcode_313
from xdis.opcodes.base import finalize_opcodes, update_pj3
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_3x.opcode_313 import opcode_arg_fmt313, opcode_extended_fmt313
from xdis.opcodes.opcode_rust.base import init_opdata_rust, make_opcodes
from xdis.version_info import PythonImplementation

_opcode = 0
version_tuple = (3, 12, 0)
python_implementation = PythonImplementation("RustPython")

# oppush[op] => number of stack entries pushed
oppush: List[int] = [0] * 256

# oppop[op] => number of stack entries popped
oppop: List[int] = [0] * 256

# opmap[opcode_name] => opcode_number
opmap: Dict[str, int] = {}

## pseudo opcodes (used in the compiler) mapped to the values
## they can become in the actual code.
_pseudo_ops = {}

_nb_ops = [
    ("NB_ADD", "+"),
    ("NB_AND", "&"),
    ("NB_FLOOR_DIVIDE", "//"),
    ("NB_LSHIFT", "<<"),
    ("NB_MATRIX_MULTIPLY", "@"),
    ("NB_MULTIPLY", "*"),
    ("NB_REMAINDER", "%"),
    ("NB_OR", "|"),
    ("NB_POWER", "**"),
    ("NB_RSHIFT", ">>"),
    ("NB_SUBTRACT", "-"),
    ("NB_TRUE_DIVIDE", "/"),
    ("NB_XOR", "^"),
    ("NB_INPLACE_ADD", "+="),
    ("NB_INPLACE_AND", "&="),
    ("NB_INPLACE_FLOOR_DIVIDE", "//="),
    ("NB_INPLACE_LSHIFT", "<<="),
    ("NB_INPLACE_MATRIX_MULTIPLY", "@="),
    ("NB_INPLACE_MULTIPLY", "*="),
    ("NB_INPLACE_REMAINDER", "%="),
    ("NB_INPLACE_OR", "|="),
    ("NB_INPLACE_POWER", "**="),
    ("NB_INPLACE_RSHIFT", ">>="),
    ("NB_INPLACE_SUBTRACT", "-="),
    ("NB_INPLACE_TRUE_DIVIDE", "/="),
    ("NB_INPLACE_XOR", "^="),
]

hasexc = []

loc = locals()

init_opdata_rust(loc, from_mod=None, version_tuple=version_tuple)

loc["opname"].extend([f"<{i}>" for i in range(256, 267)])
loc["oppop"].extend([0] * 11)
loc["oppush"].extend([0] * 11)

hasarg = []
hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasexc = []

oplists = [
    loc["hasarg"],
    loc["hasconst"],
    loc["hasname"],
    loc["hasjrel"],
    loc["hasjabs"],
    loc["haslocal"],
    loc["hascompare"],
    loc["hasfree"],
    loc["hasexc"],
]

# add new table "hasjump"
loc.update({"hasjump": []})
loc["hasjrel"] = loc["hasjump"]

make_opcodes(loc, 12897)
EXTENDED_ARG = 103

# fmt: on

# for i in range(105):
#     print(f"%3d {loc['opname'][i]}" % i)

findlinestarts = opcode_311.findlinestarts

def extended_format_BINARY_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    opname = _nb_ops[instructions[0].argval][1]
    if opname == "%":
        opname = "%%"
    elif opname == "%=":
        opname = "%%="
    return extended_format_binary_op(opc, instructions, f"%s {opname} %s")


opcode_extended_fmt313rust = {}
opcode_arg_fmt = opcode_arg_fmt13rust = {}

### update arg formatting
opcode_extended_fmt = opcode_extended_fmt312rust = {
    **opcode_extended_fmt313,
    **{
        "BINARY_OP": extended_format_BINARY_OP,
    },
}


update_pj3(globals(), loc, is_rust=True)
finalize_opcodes(loc)
