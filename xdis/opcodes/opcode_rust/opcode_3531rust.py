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

# import xdis.opcodes.opcode_313 as opcode_313
from xdis.opcodes.base import (
    VARYING_STACK_INT,
    binary_op,
    call_op,
    compare_op,
    const_op,
    def_op,
    finalize_opcodes,
    free_op,
    init_opdata,
    jabs_op,
    jrel_op,
    local_op,
    name_op,
    nargs_op,
    store_op,
    unary_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_3x.opcode_313 import opcode_arg_fmt313, opcode_extended_fmt313
from xdis.opcodes.opcode_rust.base import cmp_op as cmp_op_rust
from xdis.version_info import PythonImplementation

python_implementation = PythonImplementation("RustPython")
version_tuple = (3, 13)

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

init_opdata(loc, from_mod=None, version_tuple=version_tuple)
# Change cmp_op set in init_opdata to be Rust's version of this.
cmp_op = cmp_op_rust

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

def pseudo_op(name: str, op: int, real_ops: list):
    def_op(loc, name, op)
    _pseudo_ops[name] = real_ops
    # add the pseudo opcode to the lists its targets are in
    for oplist in oplists:
        res = [opmap[rop] in oplist for rop in real_ops]
        if any(res):
            # FIXME: for some reason JUMP_FORWARD appears to be
            # listed as a free op. It isn't.
            # if not all(res):
            #     breakpoint()
            # assert all(res)
            oplist.append(op)


# See RustPython/compiler/core/src/bytecode.rs Instruction
# fmt: off

#            OP NAME                   OPCODE   POP PUSH
#----------------------------------------------------------
def_op(loc, "BEFORE_ASYNC_WITH",            0)
binary_op(loc, "BINARY_OP",                 1,  1, 1)
binary_op(loc, "BINARY_SUBSCR",             2)
jabs_op(loc,   "BREAK_LOOP",                3,  0, 0)
varargs_op(loc, "BUILD_LIST_FROM_TUPLES",   4, 1, VARYING_STACK_INT)       # Number of list items
varargs_op(loc, "BUILD_LIST",               5, 1, VARYING_STACK_INT)       # Number of list items
varargs_op(loc, "BUILD_MAP_FOR_CALL",       6, 1, VARYING_STACK_INT)       # Number of dict entries
varargs_op(loc, "BUILD_MAP",                7, 1, VARYING_STACK_INT)       # Number of dict entries
varargs_op(loc, "BUILD_SET_FROM_TUPLES",    8, 1, VARYING_STACK_INT)       # Number of list items
varargs_op(loc, "BUILD_SET",                9, 1, VARYING_STACK_INT)       # Number of set items
def_op(loc, "BUILD_SLICE",                 10)
varargs_op(loc, "BUILD_STRING",            11, VARYING_STACK_INT)      # Number of tuple items
varargs_op(loc, "BUILD_TUPLE_FROM_ITER",   12, 1, VARYING_STACK_INT)      # Number of tuple items
varargs_op(loc, "BUILD_TUPLE_FROM_TUPLES", 13, 1, VARYING_STACK_INT)      # Number of tuple items
varargs_op(loc, "BUILD_TUPLE",             14, 1, VARYING_STACK_INT)      # Number of tuple items

call_op(loc, "CALL_FUNCTION_EX",           15)  # Flags
call_op(loc, "CALL_FUNCTION_KW",           16)
call_op(loc, "CALL_FUNCTION",              17)
call_op(loc, "CallIntrinsic1",             18)
call_op(loc, "CallIntrinsic2",             19)
call_op(loc, "CALL_METHOD_EX",             20)
call_op(loc, "CALL_METHOD_KW",             21)
call_op(loc, "CALL_METHOD",                22)
jrel_op(loc, "CHECK_EG_MATCH",             23,   0, 0)
compare_op(loc, "COMPARE_OP",              24,  2, 1)  # Comparison operator
compare_op(loc, "CONTAINS_OP",             25,  2, 1)
jabs_op(loc, "CONTINUE_LOOP",              26,  2, 1)
def_op(loc,    "ConvertValue",             27,  0, 0)
def_op(loc,    "COPY",                     28,  0, 0)

name_op(loc,   "DELETE_ATTR",              29)        # Local variable number is in operand
free_op(loc,   "DELETE_DEREF",             30,  0, 0)
local_op(loc,  "DELETE_FAST",              31,  0, 0) # Local variable number is in operand
name_op(loc,   "DELETE_GLOBAL",            32)         # ""
local_op(loc,  "DELETE_LOCAL",             33,  0, 0)
def_op(loc,    "DELETE_SUBSCR",            34,  0, 0)
varargs_op(loc, "DICT_UPDATE",             35)        # Number of dict entries

def_op(loc, "END_ASYNC_FOR",               36)
def_op(loc, "END_FINALLY",                 37)
def_op(loc, "EnterFinally",                38)
def_op(loc, "EXTENDED_ARG",                39)

jabs_op(loc, "FOR_ITER",                   40)
def_op(loc, "FormatSimple",                41, VARYING_STACK_INT, VARYING_STACK_INT)
def_op(loc, "FormatWithSpec",              42, VARYING_STACK_INT, VARYING_STACK_INT)
def_op(loc, "GET_AITER",                   43)
def_op(loc, "GET_ANEXT",                   44)
def_op(loc, "GET_AWAITABLE",               45)
def_op(loc, "GET_ITER",                    46)
def_op(loc, "GetLen",                      47)


name_op(loc,   "IMPORT_FROM",              48)
name_op(loc,   "IMPORT_NAME",              49)
def_op(loc,    "IsOp",                     50,  0, 1)

jabs_op(loc, "JUMP_IF_FALSE_OR_POP",       51) # "
jabs_op(loc, "JumpIfNotExcMatch",          52) # Number of words to skip
jabs_op(loc, "JUMP_IF_TRUE_OR_POP",        53) # Number of words to skip
jabs_op(loc,  "JUMP",                      54) # Number of words to skip

def_op(loc,   "LIST_APPEND",               55)
name_op(loc,  "LOAD_ATTR",                 56)       # Index in name list
def_op(loc,   "LOAD_BUILD_CLASS",          57)
def_op(loc,   "LOAD_CLASS_DEREF",          59)
free_op(loc,  "LOAD_CLOSURE",              59)
const_op(loc, "LOAD_CONST",                60,  0, 1)
free_op(loc,  "LOAD_DEREF",                61)
local_op(loc, "LOAD_FAST",                 62)
name_op(loc,  "LOAD_GLOBAL",               63)
def_op(loc,   "LOAD_METHOD",               64)
name_op(loc,  "LOAD_NAME",                 65)

nargs_op(loc, "MAKE_FUNCTION",             66, VARYING_STACK_INT)    # Flags
def_op(loc, "MAP_ADD",                     67)
def_op(loc, "MATCH_CLASS",                 68)
def_op(loc, "MATCH_KEYS",                  69)
def_op(loc, "MATCH_MAPPING",               70)
def_op(loc, "MATCH_SEQUENCE",              71)

def_op(loc, "NOP",                         72,  0, 0)

def_op(loc, "POP_BLOCK",                   73)
def_op(loc, "POP_EXCEPT",                  74)
jabs_op(loc, "POP_JUMP_IF_FALSE",          75)
jabs_op(loc, "POP_JUMP_IF_TRUE",           76)
def_op(loc,  "POP_TOP",                    77,  1, 0)

def_op(loc, "RAISE",                       78)
def_op(loc, "RESUME",                      79,   0, 0)
const_op(loc, "RETURN_CONST",              80)
def_op(loc, "RETURN_VALUE",                81)
def_op(loc, "REVERSE",                     82)

def_op(loc, "SET_ADD",                     83)
def_op(loc, "SET_FUNCTION_ATTR",           84)
def_op(loc, "SETUP_ANNOTATION",            85)
def_op(loc, "SETUP_ASYNC_WITH",            86, 0, 1)
def_op(loc, "SETUP_EXCEPT",                87)
jabs_op(loc, "SETUP_FINALLY",              88)
jabs_op(loc, "SETUP_LOOP",                 89)
jabs_op(loc, "SETUP_WITHP",                90)
name_op(loc,   "STORE_ATTR",               91)        # Index in name list
store_op(loc,  "STORE_DEREF",              92,  1, 0, is_type="free")
store_op(loc,  "STORE_FAST",               93,  1, 0, is_type="local")  # Local variable
name_op(loc,   "STORE_GLOBAL",             94)                           # ""
store_op(loc,  "STORE_LOCAL",              95,  4,  0)
def_op(loc,    "STORE_SUBSCR",             96,  0, 0)
binary_op(loc,  "SUBCRIPT",                97)
def_op(loc,     "SWAP",                    98,  1, 1)

compare_op(loc, "TEST_OP",                 99,  2, 1)  # test operator
def_op(loc,     "TO_BOOL",                100,  1, 1)

unary_op(loc,  "UNARY_OP",                101,  1, 1)
def_op(loc, "UNPACK_EX",                  102, VARYING_STACK_INT, VARYING_STACK_INT)
varargs_op(loc, "UNPACK_SEQUENCE",        103, 1, VARYING_STACK_INT)   # Number of tuple items

def_op(loc, "WithCleanupFinish",          104)
def_op(loc, "WithCleanupStart",           105)

def_op(loc, "YIELD",                      106)
def_op(loc, "YIELD_FROM",                 107)


EXTENDED_ARG = 103

# fmt: on

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
