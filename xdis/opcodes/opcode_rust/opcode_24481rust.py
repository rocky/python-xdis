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
RustPython 3.13 bytecode opcodes for version 0.40. There are other Rust 3.13 with different opcodes!
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
version_tuple = (3, 13)
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

make_opcodes(loc, 24881)
EXTENDED_ARG = 103

# fmt: on

# for i in range(105):
#     print(f"%3d {loc['opname'][i]}" % i)

_specializations = {
    "BINARY_OP": [
        "BINARY_OP_ADAPTIVE",
        "BINARY_OP_ADD_FLOAT",
        "BINARY_OP_ADD_INT",
        "BINARY_OP_ADD_UNICODE",
        "BINARY_OP_INPLACE_ADD_UNICODE",
        "BINARY_OP_MULTIPLY_FLOAT",
        "BINARY_OP_MULTIPLY_INT",
        "BINARY_OP_SUBTRACT_FLOAT",
        "BINARY_OP_SUBTRACT_INT",
    ],
    "BINARY_SUBSCR": [
        "BINARY_SUBSCR_ADAPTIVE",
        "BINARY_SUBSCR_DICT",
        "BINARY_SUBSCR_GETITEM",
        "BINARY_SUBSCR_LIST_INT",
        "BINARY_SUBSCR_TUPLE_INT",
    ],
    "CALL": [
        "CALL_ADAPTIVE",
        "CALL_PY_EXACT_ARGS",
        "CALL_PY_WITH_DEFAULTS",
        "CALL_BOUND_METHOD_EXACT_ARGS",
        "CALL_BUILTIN_CLASS",
        "CALL_BUILTIN_FAST_WITH_KEYWORDS",
        "CALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS",
        "CALL_NO_KW_BUILTIN_FAST",
        "CALL_NO_KW_BUILTIN_O",
        "CALL_NO_KW_ISINSTANCE",
        "CALL_NO_KW_LEN",
        "CALL_NO_KW_LIST_APPEND",
        "CALL_NO_KW_METHOD_DESCRIPTOR_FAST",
        "CALL_NO_KW_METHOD_DESCRIPTOR_NOARGS",
        "CALL_NO_KW_METHOD_DESCRIPTOR_O",
        "CALL_NO_KW_STR_1",
        "CALL_NO_KW_TUPLE_1",
        "CALL_NO_KW_TYPE_1",
    ],
    "COMPARE_OP": [
        "COMPARE_OP_ADAPTIVE",
        "COMPARE_OP_FLOAT_JUMP",
        "COMPARE_OP_INT_JUMP",
        "COMPARE_OP_STR_JUMP",
    ],
    "EXTENDED_ARG": [
        "EXTENDED_ARG_QUICK",
    ],
    "FOR_ITER": [
        "FOR_ITER_ADAPTIVE",
        "FOR_ITER_LIST",
        "FOR_ITER_RANGE",
    ],
    "JUMP_BACKWARD": [
        "JUMP_BACKWARD_QUICK",
    ],
    "LOAD_ATTR": [
        "LOAD_ATTR_ADAPTIVE",
        # These potentially push [NULL, bound method] onto the stack.
        "LOAD_ATTR_CLASS",
        "LOAD_ATTR_GETATTRIBUTE_OVERRIDDEN",
        "LOAD_ATTR_INSTANCE_VALUE",
        "LOAD_ATTR_MODULE",
        "LOAD_ATTR_PROPERTY",
        "LOAD_ATTR_SLOT",
        "LOAD_ATTR_WITH_HINT",
        # These will always push [unbound method, self] onto the stack.
        "LOAD_ATTR_METHOD_LAZY_DICT",
        "LOAD_ATTR_METHOD_NO_DICT",
        "LOAD_ATTR_METHOD_WITH_DICT",
        "LOAD_ATTR_METHOD_WITH_VALUES",
    ],
    "LOAD_CONST": [
        "LOAD_CONST__LOAD_FAST",
    ],
    "LOAD_FAST": [
        "LOAD_FAST__LOAD_CONST",
        "LOAD_FAST__LOAD_FAST",
    ],
    "LOAD_GLOBAL": [
        "LOAD_GLOBAL_ADAPTIVE",
        "LOAD_GLOBAL_BUILTIN",
        "LOAD_GLOBAL_MODULE",
    ],
    "RESUME": [
        "RESUME_QUICK",
    ],
    "STORE_ATTR": [
        "STORE_ATTR_ADAPTIVE",
        "STORE_ATTR_INSTANCE_VALUE",
        "STORE_ATTR_SLOT",
        "STORE_ATTR_WITH_HINT",
    ],
    "STORE_FAST": [
        "STORE_FAST__LOAD_FAST",
        "STORE_FAST__STORE_FAST",
    ],
    "STORE_SUBSCR": [
        "STORE_SUBSCR_ADAPTIVE",
        "STORE_SUBSCR_DICT",
        "STORE_SUBSCR_LIST_INT",
    ],
    "UNPACK_SEQUENCE": [
        "UNPACK_SEQUENCE_ADAPTIVE",
        "UNPACK_SEQUENCE_LIST",
        "UNPACK_SEQUENCE_TUPLE",
        "UNPACK_SEQUENCE_TWO_TUPLE",
    ],
}
_specialized_instructions = [
    opcode for family in _specializations.values() for opcode in family
]
_specialization_stats = [
    "success",
    "failure",
    "hit",
    "deferred",
    "miss",
    "deopt",
]

_cache_format = {
    "LOAD_GLOBAL": {
        "counter": 1,
        "index": 1,
        "module_keys_version": 2,
        "builtin_keys_version": 1,
    },
    "BINARY_OP": {
        "counter": 1,
    },
    "UNPACK_SEQUENCE": {
        "counter": 1,
    },
    "COMPARE_OP": {
        "counter": 1,
        "mask": 1,
    },
    "BINARY_SUBSCR": {
        "counter": 1,
        "type_version": 2,
        "func_version": 1,
    },
    "FOR_ITER": {
        "counter": 1,
    },
    "LOAD_ATTR": {
        "counter": 1,
        "version": 2,
        "keys_version": 2,
        "descr": 4,
    },
    "STORE_ATTR": {
        "counter": 1,
        "version": 2,
        "index": 1,
    },
    "CALL": {
        "counter": 1,
        "func_version": 2,
        "min_args": 1,
    },
    "STORE_SUBSCR": {
        "counter": 1,
    },
}

_inline_cache_entries = [
    sum(_cache_format.get(opname[opcode], {}).values()) for opcode in range(256)
]

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
