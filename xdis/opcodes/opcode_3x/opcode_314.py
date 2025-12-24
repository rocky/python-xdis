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
CPython 3.14 bytecode opcodes

This is a like Python 3.14's opcode.py with some classification
of stack usage and information for formatting instructions.
of stack usage.
"""
from xdis.opcodes.base import (
    VARYING_STACK_INT,
    binary_op,
    call_op,
    compare_op,
    const_op,
    cpython_implementation,
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
    varargs_op,
)

from . import opcode_313

version_tuple = (3, 14)
python_implementation = cpython_implementation

loc = locals()

init_opdata(loc, None, version_tuple)

# extend opcodes to cover pseudo ops
loc["opname"].extend([f"<{i}>" for i in range(256, 267)])
loc["oppop"].extend([0] * 11)
loc["oppush"].extend([0] * 11)

# fmt: off
#            OP NAME                                            OPCODE  POP  PUSH
# ---------------------------------------------------------------------------
def_op(loc,     "CACHE",                                        0,      0,  0)
def_op(loc,     "BINARY_SLICE",                                 1,      3,  1)
def_op(loc,     "BUILD_TEMPLATE",                               2,      2,  1)
local_op(loc,   "BINARY_OP_INPLACE_ADD_UNICODE",                3,      2,  0)
def_op(loc,     "CALL_FUNCTION_EX",                             4,      4,  1)
def_op(loc,     "CHECK_EG_MATCH",                               5,      2,  2)
def_op(loc,     "CHECK_EXC_MATCH",                              6,      2,  2)
def_op(loc,     "CLEANUP_THROW",                                7,      3,  2)
def_op(loc,     "DELETE_SUBSCR",                                8,      2,  0)
def_op(loc,     "END_FOR",                                      9,      1,  0)
def_op(loc,     "END_SEND",                                     10,     2,  1)
def_op(loc,     "EXIT_INIT_CHECK",                              11,     1,  0)
def_op(loc,     "FORMAT_SIMPLE",                                12,     1,  1)
def_op(loc,     "FORMAT_WITH_SPEC",                             13,     2,  1)
def_op(loc,     "GET_AITER",                                    14,     1,  1)
def_op(loc,     "GET_ANEXT",                                    15,     1,  2)
def_op(loc,     "GET_ITER",                                     16,     0,  0)
def_op(loc,     "RESERVED",                                     17,     0,  0)
def_op(loc,     "GET_LEN",                                      18,     1,  2)
def_op(loc,     "GET_YIELD_FROM_ITER",                          19,     1,  1)
def_op(loc,     "INTERPRETER_EXIT",                             20,     1,  0)
def_op(loc,     "LOAD_BUILD_CLASS",                             21,     0,  1)
def_op(loc,     "LOAD_LOCALS",                                  22,     0,  1)
def_op(loc,     "MAKE_FUNCTION",                                23,     1,  1)
def_op(loc,     "MATCH_KEYS",                                   24,     2,  3)
def_op(loc,     "MATCH_MAPPING",                                25,     1,  2)
def_op(loc,     "MATCH_SEQUENCE",                               26,     1,  2)
def_op(loc,     "NOP",                                          27,     0,  0)
def_op(loc,     "NOT_TAKEN",                                    28,     0,  0)
def_op(loc,     "POP_EXCEPT",                                   29,     1,  0)
def_op(loc,     "POP_ITER",                                     30,     1,  0)
def_op(loc,     "POP_TOP",                                      31,     1,  0)
def_op(loc,     "PUSH_EXC_INFO",                                32,     1,  2)
def_op(loc,     "PUSH_NULL",                                    33,     0,  1)
def_op(loc,     "RETURN_GENERATOR",                             34,     0,  1)
def_op(loc,     "RETURN_VALUE",                                 35,     1,  1)
def_op(loc,     "SETUP_ANNOTATIONS",                            36,     0,  0)
store_op(loc,   "STORE_SLICE",                                  37,     4,  0)
store_op(loc,   "STORE_SUBSCR",                                 38,     3,  0)
unary_op(loc,   "TO_BOOL",                                      39,     1,  1)
unary_op(loc,   "UNARY_INVERT",                                 40,     1,  1)
unary_op(loc,   "UNARY_NEGATIVE",                               41,     1,  1)
unary_op(loc,   "UNARY_NOT",                                    42,     1,  1)
def_op(loc,     "WITH_EXCEPT_START",                            43,     5,  6)
binary_op(loc,  "BINARY_OP",                                    44,     2,  1)
def_op(loc,     "BUILD_INTERPOLATION",                          45,  VARYING_STACK_INT,  1)  # Either -1 or -2:  pops 2 + (oparg & 1) and pushes result
varargs_op(loc, "BUILD_LIST",                                   46,     -1, 1)  # TOS is count of list items
varargs_op(loc, "BUILD_MAP",                                    47,     0,  1)  # argument is dictionary count to be popped
varargs_op(loc, "BUILD_SET",                                    48,     -1, 1)  # TOS is count of set items
varargs_op(loc, "BUILD_SLICE",                                  49,     -1, 1)  # TOS is slice
varargs_op(loc, "BUILD_STRING",                                 50,     -1, 1)  # TOS is concatenated strings
varargs_op(loc, "BUILD_TUPLE",                                  51,     -1, 1)  # TOS is count of tuple items
call_op(loc,    "CALL",                                         52,     VARYING_STACK_INT, 2)  # pops 2 + oparg; TOS is return value
def_op(loc,     "CALL_INTRINSIC_1",                             53,     1,  1)
def_op(loc,     "CALL_INTRINSIC_2",                             54,     2,  1)
call_op(loc,    "CALL_KW",                                      55,     -3, 1)  # pops 3 + oparg; TOS is return value
compare_op(loc, "COMPARE_OP",                                   56,     2,  1)
binary_op(loc,  "CONTAINS_OP",                                  57,     2,  1)
def_op(loc,     "CONVERT_VALUE",                                58,     1,  1)
def_op(loc,     "COPY",                                         59,     0,  1)
def_op(loc,     "COPY_FREE_VARS",                               60,     0,  0)
name_op(loc,    "DELETE_ATTR",                                  61,     1,  0)
free_op(loc,    "DELETE_DEREF",                                 62,     0,  0)
local_op(loc,   "DELETE_FAST",                                  63,     0,  0)
name_op(loc,    "DELETE_GLOBAL",                                64,     0,  0)
name_op(loc,    "DELETE_NAME",                                  65,     0,  0)
def_op(loc,     "DICT_MERGE",                                   66,     1,  0)
def_op(loc,     "DICT_UPDATE",                                  67,     1,  0)
jrel_op(loc,    "END_ASYNC_FOR",                                68,     2,  0, conditional=True)
def_op(loc,     "EXTENDED_ARG",                                 69,     0,  0)
jrel_op(loc,    "FOR_ITER",                                     70,     0,  1, conditional=True)
def_op(loc,     "GET_AWAITABLE",                                71,     1,  1)
name_op(loc,    "IMPORT_FROM",                                  72,     1,  2)
name_op(loc,    "IMPORT_NAME",                                  73,     2,  1)
compare_op(loc, "IS_OP",                                        74,     2,  1)
jrel_op(loc,    "JUMP_BACKWARD",                                75,     0,  0, conditional=False)
jrel_op(loc,    "JUMP_BACKWARD_NO_INTERRUPT",                   76,     0,  0, conditional=False)
jrel_op(loc,    "JUMP_FORWARD",                                 77,     0,  0, conditional=False)
def_op(loc,     "LIST_APPEND",                                  78,     1,  0)
def_op(loc,     "LIST_EXTEND",                                  79,     1,  0)
name_op(loc,    "LOAD_ATTR",                                    80,     1,  1)  # pops 1 + (oparg & 1)
def_op(loc,     "LOAD_COMMON_CONSTANT",                         81,     0,  1)
const_op(loc,   "LOAD_CONST",                                   82,     0,  1)
local_op(loc,   "LOAD_DEREF",                                   83,     0,  1)
local_op(loc,   "LOAD_FAST",                                    84,     0,  1)
local_op(loc,   "LOAD_FAST_AND_CLEAR",                          85,     0,  1)
local_op(loc,   "LOAD_FAST_BORROW",                             86,     0,  1)
local_op(loc,   "LOAD_FAST_BORROW_LOAD_FAST_BORROW",            87,     0,  2)
local_op(loc,   "LOAD_FAST_CHECK",                              88,     0,  1)
local_op(loc,   "LOAD_FAST_LOAD_FAST",                          89,     0,  2)
free_op(loc,    "LOAD_FROM_DICT_OR_DEREF",                      90,     1,  1)
name_op(loc,    "LOAD_FROM_DICT_OR_GLOBALS",                    91,     1,  1)
name_op(loc,    "LOAD_GLOBAL",                                  92,     0,  1)  # pops 1 + (oparg & 1)
name_op(loc,    "LOAD_NAME",                                    93,     0,  1)
def_op(loc,     "LOAD_SMALL_INT",                               94,     0,  1)
def_op(loc,     "LOAD_SPECIAL",                                 95,     1,  2)
name_op(loc,    "LOAD_SUPER_ATTR",                              96,     3,  1)  # pops 1 + (oparg & 1)
free_op(loc,    "MAKE_CELL",                                    97,     0,  0)
def_op(loc,     "MAP_ADD",                                      98,     2,  0)
def_op(loc,     "MATCH_CLASS",                                  99,     3,  1)
jrel_op(loc,    "POP_JUMP_IF_FALSE",                            100,    1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_NONE",                             101,    1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_NOT_NONE",                         102,    1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_TRUE",                             103,    1,  0, conditional=True)
varargs_op(loc, "RAISE_VARARGS",                                104,    -1, 0)
def_op(loc,     "RERAISE",                                      105,    1,  0)
jrel_op(loc,    "SEND",                                         106,    2,  2, conditional=True)
def_op(loc,     "SET_ADD",                                      107,    1,  0)
def_op(loc,     "SET_FUNCTION_ATTRIBUTE",                       108,    2,  1)
def_op(loc,     "SET_UPDATE",                                   109,    1,  0)
store_op(loc,   "STORE_ATTR",                                   110,    2,  0, is_type="name")
store_op(loc,   "STORE_DEREF",                                  111,    1,  0, is_type="free")
store_op(loc,   "STORE_FAST",                                   112,    1,  0, is_type="local")
local_op(loc,   "STORE_FAST_LOAD_FAST",                         113,    1,  1)
store_op(loc,   "STORE_FAST_STORE_FAST",                        114,    2,  0, is_type="local")
store_op(loc,   "STORE_GLOBAL",                                 115,    1,  0, is_type="name")
store_op(loc,   "STORE_NAME",                                   116,    1,  0, is_type="name")
def_op(loc,     "SWAP",                                         117,    0,  0)
varargs_op(loc, "UNPACK_EX",                                    118,    VARYING_STACK_INT, VARYING_STACK_INT)  # pushes 1 + (oparg & 0xFF) + (oparg >> 8)
varargs_op(loc, "UNPACK_SEQUENCE",                              119,    1, VARYING_STACK_INT)  # unpacks TOS, arg is the count
def_op(loc,     "YIELD_VALUE",                                  120,    1,  1)
def_op(loc,     "RESUME",                                       128,    0,  0)

# Specialized opcodes (>128)
binary_op(loc,  "BINARY_OP_ADD_FLOAT",                          129,    2,  1)
binary_op(loc,  "BINARY_OP_ADD_INT",                            130,    2,  1)
binary_op(loc,  "BINARY_OP_ADD_UNICODE",                        131,    2,  1)
binary_op(loc,  "BINARY_OP_EXTEND",                             132,    2,  1)
binary_op(loc,  "BINARY_OP_MULTIPLY_FLOAT",                     133,    2,  1)
binary_op(loc,  "BINARY_OP_MULTIPLY_INT",                       134,    2,  1)
binary_op(loc,  "BINARY_OP_SUBSCR_DICT",                        135,    2,  1)
binary_op(loc,  "BINARY_OP_SUBSCR_GETITEM",                     136,    2,  0)
binary_op(loc,  "BINARY_OP_SUBSCR_LIST_INT",                    137,    2,  1)
binary_op(loc,  "BINARY_OP_SUBSCR_LIST_SLICE",                  138,    2,  1)
binary_op(loc,  "BINARY_OP_SUBSCR_STR_INT",                     139,    2,  1)
binary_op(loc,  "BINARY_OP_SUBSCR_TUPLE_INT",                   140,    2,  1)
binary_op(loc,  "BINARY_OP_SUBTRACT_FLOAT",                     141,    2,  1)
binary_op(loc,  "BINARY_OP_SUBTRACT_INT",                       142,    2,  1)
call_op(loc,    "CALL_ALLOC_AND_ENTER_INIT",                    143,    -2, 0)  # pops 2 + oparg
call_op(loc,    "CALL_BOUND_METHOD_EXACT_ARGS",                 144,    -2, 0)  # pops 2 + oparg
call_op(loc,    "CALL_BOUND_METHOD_GENERAL",                    145,    -2, 0)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_CLASS",                           146,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_FAST",                            147,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_FAST_WITH_KEYWORDS",              148,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_O",                               149,    -2, 1)  # pops 2 + oparg
def_op(loc,     "CALL_ISINSTANCE",                              150,    4,  1)
call_op(loc,    "CALL_KW_BOUND_METHOD",                         151,    -3, 0)  # pops 3 + oparg
call_op(loc,    "CALL_KW_NON_PY",                               152,    -3, 1)  # pops 3 + oparg
call_op(loc,    "CALL_KW_PY",                                   153,    -3, 0)  # pops 3 + oparg
def_op(loc,     "CALL_LEN",                                     154,    3,  1)
def_op(loc,     "CALL_LIST_APPEND",                             155,    3,  0)
call_op(loc,    "CALL_METHOD_DESCRIPTOR_FAST",                  156,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS",    157,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_NOARGS",                158,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_O",                     159,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_NON_PY_GENERAL",                          160,    -2, 1)  # pops 2 + oparg
call_op(loc,    "CALL_PY_EXACT_ARGS",                           161,    -2, 0)  # pops 2 + oparg
call_op(loc,    "CALL_PY_GENERAL",                              162,    -2, 0)  # pops 2 + oparg
def_op(loc,     "CALL_STR_1",                                   163,    3,  1)
def_op(loc,     "CALL_TUPLE_1",                                 164,    3,  1)
def_op(loc,     "CALL_TYPE_1",                                  165,    3,  1)
compare_op(loc, "COMPARE_OP_FLOAT",                             166,    2,  1)
compare_op(loc, "COMPARE_OP_INT",                               167,    2,  1)
compare_op(loc, "COMPARE_OP_STR",                               168,    2,  1)
def_op(loc,     "CONTAINS_OP_DICT",                             169,    2,  1)
def_op(loc,     "CONTAINS_OP_SET",                              170,    2,  1)
jrel_op(loc,    "FOR_ITER_GEN",                                 171,    2,  2, conditional=True)
jrel_op(loc,    "FOR_ITER_LIST",                                172,    2,  3, conditional=True)
jrel_op(loc,    "FOR_ITER_RANGE",                               173,    2,  3, conditional=True)
jrel_op(loc,    "FOR_ITER_TUPLE",                               174,    2,  3, conditional=True)
jrel_op(loc,    "JUMP_BACKWARD_JIT",                            175,    0,  0, conditional=False)
jrel_op(loc,    "JUMP_BACKWARD_NO_JIT",                         176,    0,  0, conditional=False)
def_op(loc,     "LOAD_ATTR_CLASS",                              177,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_CLASS_WITH_METACLASS_CHECK",         178,    1,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_ATTR_GETATTRIBUTE_OVERRIDDEN",            179,    1,  1)
def_op(loc,     "LOAD_ATTR_INSTANCE_VALUE",                     180,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_METHOD_LAZY_DICT",                   181,    1,  2)
def_op(loc,     "LOAD_ATTR_METHOD_NO_DICT",                     182,    1,  2)
def_op(loc,     "LOAD_ATTR_METHOD_WITH_VALUES",                 183,    1,  2)
def_op(loc,     "LOAD_ATTR_MODULE",                             184,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_NONDESCRIPTOR_NO_DICT",              185,    1,  1)
def_op(loc,     "LOAD_ATTR_NONDESCRIPTOR_WITH_VALUES",          186,    1,  1)
def_op(loc,     "LOAD_ATTR_PROPERTY",                           187,    1,  0)
def_op(loc,     "LOAD_ATTR_SLOT",                               188,    1,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_ATTR_WITH_HINT",                          189,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_GLOBAL_BUILTIN",                          190,    0,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_GLOBAL_MODULE",                           191,    0,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_SUPER_ATTR_ATTR",                         192,    3,  1)
name_op(loc,    "LOAD_SUPER_ATTR_METHOD",                       193,    3,  2)
def_op(loc,     "RESUME_CHECK",                                 194,    0,  0)
def_op(loc,     "SEND_GEN",                                     195,    2,  1)
def_op(loc,     "STORE_ATTR_INSTANCE_VALUE",                    196,    2,  0)
def_op(loc,     "STORE_ATTR_SLOT",                              197,    2,  0)
store_op(loc,   "STORE_ATTR_WITH_HINT",                         198,    2,  0, is_type="name")
def_op(loc,     "STORE_SUBSCR_DICT",                            199,    3,  0)
def_op(loc,     "STORE_SUBSCR_LIST_INT",                        200,    3,  0)
def_op(loc,     "TO_BOOL_ALWAYS_TRUE",                          201,    1,  1)
def_op(loc,     "TO_BOOL_BOOL",                                 202,    1,  1)
def_op(loc,     "TO_BOOL_INT",                                  203,    1,  1)
def_op(loc,     "TO_BOOL_LIST",                                 204,    1,  1)
def_op(loc,     "TO_BOOL_NONE",                                 205,    1,  1)
def_op(loc,     "TO_BOOL_STR",                                  206,    1,  1)
varargs_op(loc, "UNPACK_SEQUENCE_LIST",                         207,    1,  -1)
varargs_op(loc, "UNPACK_SEQUENCE_TUPLE",                        208,    1,  -1)
def_op(loc,     "UNPACK_SEQUENCE_TWO_TUPLE",                    209,    1,  2)
def_op(loc,     "INSTRUMENTED_END_FOR",                         233,    3,  2)
def_op(loc,     "INSTRUMENTED_POP_ITER",                        234,    1,  0)
def_op(loc,     "INSTRUMENTED_END_SEND",                        235,    2,  1)
jrel_op(loc,    "INSTRUMENTED_FOR_ITER",                        236,    2,  1, conditional=True)
def_op(loc,     "INSTRUMENTED_INSTRUCTION",                     237,    0,  1)
jrel_op(loc,    "INSTRUMENTED_JUMP_FORWARD",                    238,    0,  0, conditional=False)
def_op(loc,     "INSTRUMENTED_NOT_TAKEN",                       239,    0,  0)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_TRUE",                240,    0,  0, conditional=True)  # dunno why it's not 1, 0.
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_FALSE",               241,    1,  0, conditional=True)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_NONE",                242,    1,  0, conditional=True)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_NOT_NONE",            243,    1,  0, conditional=True)
def_op(loc,     "INSTRUMENTED_RESUME",                          244,    1,  0)  # dunno why it's not 0, 0.
def_op(loc,     "INSTRUMENTED_RETURN_VALUE",                    245,    1,  1)
def_op(loc,     "INSTRUMENTED_YIELD_VALUE",                     246,    1,  1)
jrel_op(loc,    "INSTRUMENTED_END_ASYNC_FOR",                   247,    0,  0, conditional=True) # dunnow why it's not 2, 0
name_op(loc,    "INSTRUMENTED_LOAD_SUPER_ATTR",                 248,    VARYING_STACK_INT,  1)  # pushes 1 + (oparg & 1)
call_op(loc,    "INSTRUMENTED_CALL",                            249,    -2, 1)
call_op(loc,    "INSTRUMENTED_CALL_KW",                         250,    -3, 1)
def_op(loc,     "INSTRUMENTED_CALL_FUNCTION_EX",                251,    4,  1)
jrel_op(loc,    "INSTRUMENTED_JUMP_BACKWARD",                   252,    0,  0, conditional=False)
def_op(loc,     "INSTRUMENTED_LINE",                            253,    0,  0)
def_op(loc,     "ENTER_EXECUTOR",                               254,    0,  0)
def_op(loc,     "TRACE_RECORD",                                 255,    0,  0)
def_op(loc,     "ANNOTATIONS_PLACEHOLDER",                      256,    0,  0)
jrel_op(loc,    "JUMP",                                         257,    0,  0, conditional=False)
jrel_op(loc,    "JUMP_IF_FALSE",                                258,    1,  1, conditional=True)
jrel_op(loc,    "JUMP_IF_TRUE",                                 259,    1,  1, conditional=True)
jrel_op(loc,    "JUMP_NO_INTERRUPT",                            260,    0,  0, conditional=False)
local_op(loc,   "LOAD_CLOSURE",                                 261,    0,  1)
def_op(loc,     "POP_BLOCK",                                    262,    0,  0)
def_op(loc,     "SETUP_CLEANUP",                                263,    0,  2)
def_op(loc,     "SETUP_FINALLY",                                264,    0,  1)
def_op(loc,     "SETUP_WITH",                                   265,    0,  1)
def_op(loc,     "STORE_FAST_MAYBE_NULL",                        266,    1,  0)

# ops >= 44 have args
HAVE_ARGUMENT = 44

loc["hasarg"] = [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 128, 143, 144, 145, 146, 147, 148, 149, 151, 152, 153, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 195, 198, 207, 208, 209, 236, 238, 240, 241, 242, 243, 244, 246, 247, 248, 249, 250, 252, 254, 255, 257, 258, 259, 260, 261, 263, 264, 265, 266]
# hasconst table populated by const_op definitions
# hasname table populated by name_op and store_op definitions
# jrel table populated by jrel_op definitions
loc["hasjabs"] = []
loc["hasjump"] = loc["hasjrel"]
# hasfree table populated by free_op and store_op definitions
# haslocal table populated by local_op and store_op definitions
loc["hasexc"] = [263, 264, 265]

# fmt: on

### update formatting
from xdis.opcodes.format.extended import extended_format_binary_op

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
    ("NB_SUBSCR", "[]"),
]


def format_BINARY_OP_314(arg: int):
    return _nb_ops[arg][1]


def extended_BINARY_OP_314(opc, instructions):
    opname = _nb_ops[instructions[0].argval][1]

    fmt_str = "%s[%s]" if opname == "[]" else f"%s {opname} %s"
    return extended_format_binary_op(opc, instructions, fmt_str)


_common_constants = ("AssertionError", "NotImplementedError", "tuple", "all", "any")


def format_LOAD_COMMON_CONSTANT_314(arg: int):
    return _common_constants[arg]
    return _common_constants[arg]


opcode_arg_fmt = opcode_arg_fmt314 = {
    **opcode_313.opcode_arg_fmt313,
    **{"BINARY_OP": format_BINARY_OP_314},
    **{"LOAD_COMMON_CONSTANT": format_LOAD_COMMON_CONSTANT_314},
}

opcode_extended_fmt = opcode_extended_fmt314 = {
    **opcode_313.opcode_extended_fmt313,
    **{"BINARY_OP": extended_BINARY_OP_314},
}

# CALL_FUNCTION_EX no longer takes an argument in 3.14, so it no longer needs to be formatted
del opcode_arg_fmt["CALL_FUNCTION_EX"]

findlinestarts = opcode_313.findlinestarts_313

update_pj3(globals(), loc)
finalize_opcodes(loc)
