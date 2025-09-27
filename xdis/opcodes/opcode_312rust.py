"""
RustPython 3.12 bytecode opcodes

"""

#FIXME: this needs a lot of going over.

from typing import Dict, List, Optional, Tuple

import xdis.opcodes.opcode_313 as opcode_313
from xdis.opcodes.base import (
    binary_op,
    compare_op,
    const_op,
    def_op,
    finalize_opcodes,
    free_op,
    init_opdata,
    jrel_op,
    local_op,
    name_op,
    store_op,
    unary_op,
    update_pj3,
)
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_312 import opcode_arg_fmt312, opcode_extended_fmt312

version_tuple = (3, 12)
python_implementation = "RustPython"

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

init_opdata(loc, opcode_313, version_tuple)

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


# fmt: off

#            OP NAME                         OPCODE  POP PUSH
#----------------------------------------------------------
def_op(loc,    "CACHE",                     0,      0,   0)
def_op(loc,    "POP_TOP",                   1,      1,   0)
def_op(loc,    "PUSH_NULL",                 2,      0 ,  1)

def_op(loc,    "NOP",                       9,      0,   0)
unary_op(loc,  "UNARY_POSITIVE",           10)
unary_op(loc,  "UNARY_NEGATIVE",           11)
unary_op(loc,  "UNARY_NOT",                12)

unary_op(loc,  "UNARY_INVERT",             15)

binary_op(loc, "BINARY_SUBSCR",            25)
binary_op(loc, "BINARY_SLICE",             26)
store_op(loc,  "STORE_SLICE",              27,       4,  0)

def_op(loc,    "GET_LEN",                  30,       0,  1)
def_op(loc,    "MATCH_MAPPING",            31,   0, 1)
def_op(loc,    "MATCH_SEQUENCE",           32,   0, 1)
def_op(loc,    "MATCH_KEYS",               33,   0, 2)

jrel_op(loc, "PUSH_EXC_INFO",              35,   0, 1)
def_op(loc, "CHECK_EXC_MATCH", 36)
jrel_op(loc, "CHECK_EG_MATCH",             37,   0, 0)

# FIXME: fill in
def_op(loc, "WITH_EXCEPT_START", 49)
def_op(loc, "GET_AITER", 50)
def_op(loc, "GET_ANEXT", 51)
def_op(loc, "BEFORE_ASYNC_WITH", 52)
def_op(loc, "BEFORE_WITH", 53)
def_op(loc, "END_ASYNC_FOR", 54)
def_op(loc, "CLEANUP_THROW", 55)

def_op(loc, "STORE_SUBSCR", 60)
def_op(loc, "DELETE_SUBSCR", 61)

# TODO: RUSTPYTHON
# Delete below def_op after updating coroutines.py
def_op(loc, "YIELD_FROM", 72)

def_op(loc, "GET_ITER", 68)
def_op(loc, "GET_YIELD_FROM_ITER", 69)
def_op(loc, "PRINT_EXPR", 70)
def_op(loc, "LOAD_BUILD_CLASS", 71)

def_op(loc, "LOAD_ASSERTION_ERROR", 74)
def_op(loc, "RETURN_GENERATOR", 75)

def_op(loc, "LIST_TO_TUPLE", 82)
def_op(loc, "RETURN_VALUE", 83)
def_op(loc, "IMPORT_STAR", 84)
def_op(loc, "SETUP_ANNOTATIONS", 85)

def_op(loc, "ASYNC_GEN_WRAP", 87)
def_op(loc, "PREP_RERAISE_STAR", 88)
def_op(loc, "POP_EXCEPT", 89)

HAVE_ARGUMENT = 90             # real opcodes from here have an argument:

name_op(loc, "STORE_NAME", 90)       # Index in name list
name_op(loc, "DELETE_NAME", 91)      # ""
def_op(loc, "UNPACK_SEQUENCE", 92)   # Number of tuple items
jrel_op(loc, "FOR_ITER", 93)
def_op(loc, "UNPACK_EX", 94)
name_op(loc, "STORE_ATTR", 95)       # Index in name list
name_op(loc, "DELETE_ATTR", 96)      # ""
name_op(loc, "STORE_GLOBAL", 97)     # ""
name_op(loc, "DELETE_GLOBAL", 98)    # ""

def_op(loc, "SWAP",                            99,   0, 0)

# Operand is in const list
const_op(loc,   "LOAD_CONST",                 100,   0, 1)

name_op(loc, "LOAD_NAME", 101)       # Index in name list
def_op(loc, "BUILD_TUPLE", 102)      # Number of tuple items
def_op(loc, "BUILD_LIST", 103)       # Number of list items
def_op(loc, "BUILD_SET", 104)        # Number of set items
def_op(loc, "BUILD_MAP", 105)        # Number of dict entries
name_op(loc, "LOAD_ATTR", 106)       # Index in name list
compare_op(loc, "COMPARE_OP",        107,  2,  1)  # Comparison operator
name_op(loc, "IMPORT_NAME", 108)     # Index in name list
name_op(loc, "IMPORT_FROM", 109)     # Index in name list
jrel_op(loc, "JUMP_FORWARD", 110)    # Number of words to skip
jrel_op(loc, "JUMP_IF_FALSE_OR_POP", 111) # Number of words to skip
jrel_op(loc, "JUMP_IF_TRUE_OR_POP", 112)  # ""
jrel_op(loc, "POP_JUMP_IF_FALSE", 114)
jrel_op(loc, "POP_JUMP_IF_TRUE", 115)
name_op(loc, "LOAD_GLOBAL", 116)     # Index in name list
def_op(loc, "IS_OP", 117)
def_op(loc, "CONTAINS_OP", 118)
def_op(loc, "RERAISE",                 119,   3, 0)
def_op(loc, "COPY", 120)
def_op(loc, "BINARY_OP", 122)
jrel_op(loc, "SEND", 123) # Number of bytes to skip
local_op(loc, "LOAD_FAST",            124,  0,  1)  # Local variable number
loc["nullaryloadop"].add(124)
store_op(loc, "STORE_FAST",           125,  1,  0, is_type="local")  # Local variable
local_op(loc, "DELETE_FAST",          126,  0,  0) # Local variable number is in operand
def_op(loc    , "LOAD_FAST_CHECK"                  , 127,   0, 1)
local_op(loc, "LOAD_FAST_CHECK", 127)  # Local variable number
jrel_op(loc, "POP_JUMP_IF_NOT_NONE", 128)
jrel_op(loc, "POP_JUMP_IF_NONE", 129)
def_op(loc, "RAISE_VARARGS", 130)    # Number of raise arguments (1, 2, or 3)
def_op(loc, "GET_AWAITABLE", 131)
def_op(loc, "MAKE_FUNCTION", 132)    # Flags
def_op(loc, "BUILD_SLICE", 133)      # Number of items
jrel_op(loc, "JUMP_BACKWARD_NO_INTERRUPT", 134) # Number of words to skip (backwards)
free_op(loc, "MAKE_CELL",                     135,   0, 0)
free_op(loc, "LOAD_CLOSURE", 136)
free_op(loc, "LOAD_DEREF",                    137,   0, 1)
loc["nullaryop"].add(137)
loc["nullaryloadop"].add(137)
store_op(loc, "STORE_DEREF",                  138,   1, 0, is_type="free")
free_op(loc, "DELETE_DEREF",                  139,   0, 0)
jrel_op(loc, "JUMP_BACKWARD", 140)    # Number of words to skip (backwards)

def_op(loc, "CALL_FUNCTION_EX", 142)  # Flags

def_op(loc, "EXTENDED_ARG", 144)
EXTENDED_ARG = 144
def_op(loc, "LIST_APPEND", 145)
def_op(loc, "SET_ADD", 146)
def_op(loc, "MAP_ADD", 147)
free_op(loc, "LOAD_CLASSDEREF", 148)
def_op(loc, "COPY_FREE_VARS", 149)
def_op(loc, "YIELD_VALUE", 150)

# This must be kept in sync with deepfreeze.py
# resume, acts like a nop
def_op(loc, "RESUME",                         151,   0, 0)

def_op(loc, "MATCH_CLASS", 152)

def_op(loc, "FORMAT_VALUE", 155)
def_op(loc, "BUILD_CONST_KEY_MAP", 156)
def_op(loc, "BUILD_STRING", 157)

def_op(loc, "LIST_EXTEND", 162)
def_op(loc, "SET_UPDATE", 163)
def_op(loc, "DICT_MERGE", 164)
def_op(loc, "DICT_UPDATE", 165)

def_op(loc, "CALL", 171)
const_op(loc, "KW_NAMES", 172)


loc["hasarg"].extend([op for op in opmap.values() if op >= HAVE_ARGUMENT])

MIN_PSEUDO_OPCODE = 256

pseudo_op("SETUP_FINALLY", 256, ["NOP"])
hasexc.append(256)
pseudo_op("SETUP_CLEANUP", 257, ["NOP"])
hasexc.append(257)
pseudo_op("SETUP_WITH", 258, ["NOP"])
hasexc.append(258)
pseudo_op("POP_BLOCK", 259, ["NOP"])

pseudo_op("JUMP", 260, ["JUMP_FORWARD", "JUMP_BACKWARD"])
pseudo_op("JUMP_NO_INTERRUPT", 261, ["JUMP_FORWARD", "JUMP_BACKWARD_NO_INTERRUPT"])

pseudo_op("LOAD_METHOD", 262, ["LOAD_ATTR"])

# fmt: on

MAX_PSEUDO_OPCODE = MIN_PSEUDO_OPCODE + len(_pseudo_ops) - 1

# extend opcodes to cover pseudo ops

opname = [f"<{op!r}>" for op in range(MAX_PSEUDO_OPCODE + 1)]
opname.extend([f"<{i}>" for i in range(256, 267)])
oppop.extend([0] * 11)
oppush.extend([0] * 11)

for op, i in opmap.items():
    opname[i] = op


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


def extended_format_BINARY_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    opname = _nb_ops[instructions[0].argval][1]
    if opname == "%":
        opname = "%%"
    elif opname == "%=":
        opname = "%%="
    return extended_format_binary_op(opc, instructions, f"%s {opname} %s")


pcode_extended_fmt312rust = opcode_extended_fmt312.copy()
opcode_arg_fmt = opcode_arg_fmt12rust = opcode_arg_fmt312.copy()

### update arg formatting
opcode_extended_fmt = opcode_extended_fmt312rust = {
    **opcode_extended_fmt312,
    **{
        "BINARY_OP": extended_format_BINARY_OP,
    },
}

from xdis.opcodes.opcode_311 import findlinestarts

update_pj3(globals(), loc)
finalize_opcodes(loc)
