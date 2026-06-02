# (C) Copyright 2026 by Rocky Bernstein
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
CPython 3.15 bytecode opcodes

This is like Python 3.15's opcode.py with some classification
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
    nargs_op,
    store_op,
    unary_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_3x import opcode_314

version_tuple = (3, 15)
python_implementation = cpython_implementation

loc = locals()

init_opdata(loc, None, version_tuple)

# extend opcodes to cover pseudo ops
loc["opname"].extend(["<%s>" % i for i in range(256, 267)])
loc["oppop"].extend([0] * 11)
loc["oppush"].extend([0] * 11)

# fmt: off
#               OP NAME                                         OPCODE  POP  PUSH
# ---------------------------------------------------------------------------
def_op(loc,     "CACHE",                                        0,      0,  0)
def_op(loc,     "BINARY_SLICE",                                 1,      3,  1)
def_op(loc,     "BUILD_TEMPLATE",                               2,      2,  1)
local_op(loc,   "BINARY_OP_INPLACE_ADD_UNICODE",                3,      2,  0,  include_in_dis_has_table=False)
def_op(loc,     "CALL_FUNCTION_EX",                             4,      4,  1)
def_op(loc,     "CHECK_EG_MATCH",                               5,      2,  2)
def_op(loc,     "CHECK_EXC_MATCH",                              6,      2,  2)
def_op(loc,     "CLEANUP_THROW",                                7,      3,  2)
def_op(loc,     "DELETE_SUBSCR",                                8,      2,  0)
def_op(loc,     "END_FOR",                                      9,      1,  0)
def_op(loc,     "END_SEND",                                     10,     2,  0)
def_op(loc,     "EXIT_INIT_CHECK",                              11,     1,  0)
def_op(loc,     "FORMAT_SIMPLE",                                12,     1,  1)
def_op(loc,     "FORMAT_WITH_SPEC",                             13,     2,  1)
def_op(loc,     "GET_AITER",                                    14,     1,  1)
def_op(loc,     "GET_ANEXT",                                    15,     1,  2)
def_op(loc,     "GET_LEN",                                      16,     1,  2)
def_op(loc,     "RESERVED",                                     17,     0,  0)
def_op(loc,     "INTERPRETER_EXIT",                             18,     1,  0)
def_op(loc,     "LOAD_BUILD_CLASS",                             19,     0,  1)
def_op(loc,     "LOAD_LOCALS",                                  20,     0,  1) # Pushes a reference to the locals of the current scope.
                                                                               # This is not a name op.
nargs_op(loc,   "MAKE_FUNCTION",                                21,     VARYING_STACK_INT,  1)
def_op(loc,     "MATCH_KEYS",                                   22,     2,  3)
def_op(loc,     "MATCH_MAPPING",                                23,     1,  2)
def_op(loc,     "MATCH_SEQUENCE",                               24,     1,  2)
def_op(loc,     "NOP",                                          25,     0,  0)
def_op(loc,     "NOT_TAKEN",                                    26,     0,  0)
def_op(loc,     "POP_EXCEPT",                                   27,     1,  0)
def_op(loc,     "POP_ITER",                                     28,     2,  0)
def_op(loc,     "POP_TOP",                                      29,     1,  0)
def_op(loc,     "PUSH_EXC_INFO",                                30,     1,  2)
def_op(loc,     "PUSH_NULL",                                    31,     0,  1)
def_op(loc,     "RETURN_GENERATOR",                             32,     0,  1)
def_op(loc,     "RETURN_VALUE",                                 33,     1,  1)
def_op(loc,     "SETUP_ANNOTATIONS",                            34,     0,  0)
store_op(loc,   "STORE_SLICE",                                  35,     4,  0)
store_op(loc,   "STORE_SUBSCR",                                 36,     3,  0)
unary_op(loc,   "TO_BOOL",                                      37,     1,  1)
unary_op(loc,   "UNARY_INVERT",                                 38,     1,  1)
unary_op(loc,   "UNARY_NEGATIVE",                               39,     1,  1)
unary_op(loc,   "UNARY_NOT",                                    40,     1,  1)
def_op(loc,     "WITH_EXCEPT_START",                            41,     5,  6)
binary_op(loc,  "BINARY_OP",                                    42,     2,  1)
def_op(loc,     "BUILD_INTERPOLATION",                          43,  VARYING_STACK_INT,  1)  # Either -1 or -2:  pops 2 + (oparg & 1) and pushes result
varargs_op(loc, "BUILD_LIST",                                   44,     -1, 1)  # TOS is count of list items
varargs_op(loc, "BUILD_MAP",                                    45,     0,  1)  # argument is dictionary count to be popped
varargs_op(loc, "BUILD_SET",                                    46,     -1, 1)  # TOS is count of set items
varargs_op(loc, "BUILD_SLICE",                                  47,     -1, 1)  # TOS is slice
varargs_op(loc, "BUILD_STRING",                                 48,     -1, 1)  # TOS is concatenated strings
varargs_op(loc, "BUILD_TUPLE",                                  49,     -1, 1)  # TOS is count of tuple items
call_op(loc,    "CALL",                                         50,     VARYING_STACK_INT, 2)  # pops 2 + oparg; TOS is return value
def_op(loc,     "CALL_INTRINSIC_1",                             51,     1,  1)
def_op(loc,     "CALL_INTRINSIC_2",                             52,     2,  1)
call_op(loc,    "CALL_KW",                                      53,     -3, 1)  # pops 3 + oparg; TOS is return value
compare_op(loc, "COMPARE_OP",                                   54,     2,  1)
binary_op(loc,  "CONTAINS_OP",                                  55,     2,  1)
def_op(loc,     "CONVERT_VALUE",                                56,     1,  1)
def_op(loc,     "COPY",                                         57,     0,  1)
def_op(loc,     "COPY_FREE_VARS",                               58,     0,  0)
name_op(loc,    "DELETE_ATTR",                                  59,     1,  0)
free_op(loc,    "DELETE_DEREF",                                 60,     0,  0)
local_op(loc,   "DELETE_FAST",                                  61,     0,  0)
name_op(loc,    "DELETE_GLOBAL",                                62,     0,  0)
name_op(loc,    "DELETE_NAME",                                  63,     0,  0)
def_op(loc,     "DICT_MERGE",                                   64,     1,  0)
def_op(loc,     "DICT_UPDATE",                                  65,     1,  0)
jrel_op(loc,    "END_ASYNC_FOR",                                66,     2,  0, conditional=True)
def_op(loc,     "EXTENDED_ARG",                                 67,     0,  0)
jrel_op(loc,    "FOR_ITER",                                     68,     0,  1, conditional=True)
def_op(loc,     "GET_AWAITABLE",                                69,     1,  1)
def_op(loc,     "GET_ITER",                                     70,     0,  1)
name_op(loc,    "IMPORT_FROM",                                  71,     1,  2)
name_op(loc,    "IMPORT_NAME",                                  72,     2,  1)
compare_op(loc, "IS_OP",                                        73,     2,  1,  include_in_dis_has_table=False)
jrel_op(loc,    "JUMP_BACKWARD",                                74,     0,  0, conditional=False)
jrel_op(loc,    "JUMP_BACKWARD_NO_INTERRUPT",                   75,     0,  0, conditional=False)
jrel_op(loc,    "JUMP_FORWARD",                                 76,     0,  0, conditional=False)
def_op(loc,     "LIST_APPEND",                                  77,     1,  0)
def_op(loc,     "LIST_EXTEND",                                  78,     1,  0)
name_op(loc,    "LOAD_ATTR",                                    79,     1,  1)  # pops 1 + (oparg & 1)
def_op(loc,     "LOAD_COMMON_CONSTANT",                         80,     0,  1)
const_op(loc,   "LOAD_CONST",                                   81,     0,  1)
local_op(loc,   "LOAD_DEREF",                                   82,     0,  1)
local_op(loc,   "LOAD_FAST",                                    83,     0,  1)
local_op(loc,   "LOAD_FAST_AND_CLEAR",                          84,     0,  1)
local_op(loc,   "LOAD_FAST_BORROW",                             85,     0,  1)
local_op(loc,   "LOAD_FAST_BORROW_LOAD_FAST_BORROW",            86,     0,  2)
local_op(loc,   "LOAD_FAST_CHECK",                              87,     0,  1)
local_op(loc,   "LOAD_FAST_LOAD_FAST",                          88,     0,  2)
free_op(loc,    "LOAD_FROM_DICT_OR_DEREF",                      89,     1,  1)
name_op(loc,    "LOAD_FROM_DICT_OR_GLOBALS",                    90,     1,  1)
name_op(loc,    "LOAD_GLOBAL",                                  91,     0,  1)  # pops 1 + (oparg & 1)
name_op(loc,    "LOAD_NAME",                                    92,     0,  1)
def_op(loc,     "LOAD_SMALL_INT",                               93,     0,  1)
def_op(loc,     "LOAD_SPECIAL",                                 94,     1,  2)
name_op(loc,    "LOAD_SUPER_ATTR",                              95,     3,  1)  # pops 1 + (oparg & 1)
free_op(loc,    "MAKE_CELL",                                    96,     0,  0)
def_op(loc,     "MAP_ADD",                                      97,     2,  0)
def_op(loc,     "MATCH_CLASS",                                  98,     3,  1)
jrel_op(loc,    "POP_JUMP_IF_FALSE",                            99,     1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_NONE",                             100,    1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_NOT_NONE",                         101,    1,  0, conditional=True)
jrel_op(loc,    "POP_JUMP_IF_TRUE",                             102,    1,  0, conditional=True)
varargs_op(loc, "RAISE_VARARGS",                                103,    -1, 0)
def_op(loc,     "RERAISE",                                      104,    1,  0)
jrel_op(loc,    "SEND",                                         105,    2,  2, conditional=True)
def_op(loc,     "SET_ADD",                                      106,    1,  0)
def_op(loc,     "SET_FUNCTION_ATTRIBUTE",                       107,    2,  1)
def_op(loc,     "SET_UPDATE",                                   108,    1,  0)
store_op(loc,   "STORE_ATTR",                                   109,    2,  0, is_type="name")
store_op(loc,   "STORE_DEREF",                                  110,    1,  0, is_type="free")
store_op(loc,   "STORE_FAST",                                   111,    1,  0, is_type="local")
local_op(loc,   "STORE_FAST_LOAD_FAST",                         112,    1,  1)
store_op(loc,   "STORE_FAST_STORE_FAST",                        113,    2,  0, is_type="local")
store_op(loc,   "STORE_GLOBAL",                                 114,    1,  0, is_type="name")
store_op(loc,   "STORE_NAME",                                   115,    1,  0, is_type="name")
def_op(loc,     "SWAP",                                         116,    0,  0)
varargs_op(loc, "UNPACK_EX",                                    117,    VARYING_STACK_INT, VARYING_STACK_INT)  # pushes 1 + (oparg & 0xFF) + (oparg >> 8)
varargs_op(loc, "UNPACK_SEQUENCE",                              118,    1, VARYING_STACK_INT)  # unpacks TOS, arg is the count
def_op(loc,     "YIELD_VALUE",                                  119,    1,  1)
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
binary_op(loc,  "BINARY_OP_SUBSCR_USTR_INT",                    141,    2,  1)
binary_op(loc,  "BINARY_OP_SUBTRACT_FLOAT",                     142,    2,  1)
binary_op(loc,  "BINARY_OP_SUBTRACT_INT",                       143,    2,  1)
call_op(loc,    "CALL_ALLOC_AND_ENTER_INIT",                    144,    -2, 0,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BOUND_METHOD_EXACT_ARGS",                 145,    -2, 0,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BOUND_METHOD_GENERAL",                    146,    -2, 0,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_CLASS",                           147,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_FAST",                            148,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_FAST_WITH_KEYWORDS",              149,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_BUILTIN_O",                               150,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
def_op(loc,     "CALL_EX_NON_PY_GENERAL",                       151,    4,  1)
def_op(loc,     "CALL_EX_PY",                                   152,    4,  0)
def_op(loc,     "CALL_ISINSTANCE",                              153,    4,  1)
call_op(loc,    "CALL_KW_BOUND_METHOD",                         154,    -3, 0,  include_in_dis_has_table=False)  # pops 3 + oparg
call_op(loc,    "CALL_KW_NON_PY",                               155,    -3, 1,  include_in_dis_has_table=False)  # pops 3 + oparg
call_op(loc,    "CALL_KW_PY",                                   156,    -3, 0,  include_in_dis_has_table=False)  # pops 3 + oparg
def_op(loc,     "CALL_LEN",                                     157,    3,  1)
def_op(loc,     "CALL_LIST_APPEND",                             158,    3,  1)
call_op(loc,    "CALL_METHOD_DESCRIPTOR_FAST",                  159,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS",    160,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_NOARGS",                161,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_METHOD_DESCRIPTOR_O",                     162,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_NON_PY_GENERAL",                          163,    -2, 1,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_PY_EXACT_ARGS",                           164,    -2, 0,  include_in_dis_has_table=False)  # pops 2 + oparg
call_op(loc,    "CALL_PY_GENERAL",                              165,    -2, 0,  include_in_dis_has_table=False)  # pops 2 + oparg
def_op(loc,     "CALL_STR_1",                                   166,    3,  1)
def_op(loc,     "CALL_TUPLE_1",                                 167,    3,  1)
def_op(loc,     "CALL_TYPE_1",                                  168,    3,  1)
compare_op(loc, "COMPARE_OP_FLOAT",                             169,    2,  1,  include_in_dis_has_table=False)
compare_op(loc, "COMPARE_OP_INT",                               170,    2,  1,  include_in_dis_has_table=False)
compare_op(loc, "COMPARE_OP_STR",                               171,    2,  1,  include_in_dis_has_table=False)
def_op(loc,     "CONTAINS_OP_DICT",                             172,    2,  1)
def_op(loc,     "CONTAINS_OP_SET",                              173,    2,  1)
jrel_op(loc,    "FOR_ITER_GEN",                                 174,    2,  2, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "FOR_ITER_LIST",                                175,    2,  3, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "FOR_ITER_RANGE",                               176,    2,  3, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "FOR_ITER_TUPLE",                               177,    2,  3, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "FOR_ITER_VIRTUAL",                             178,    2,  3, conditional=True, include_in_dis_has_table=False)
def_op(loc,     "GET_ITER_SELF",                                179,    1,  2)
def_op(loc,     "GET_ITER_VIRTUAL",                             180,    1,  2)
jrel_op(loc,    "JUMP_BACKWARD_JIT",                            181,    0,  0, conditional=False, include_in_dis_has_table=False)
jrel_op(loc,    "JUMP_BACKWARD_NO_JIT",                         182,    0,  0, conditional=False, include_in_dis_has_table=False)
def_op(loc,     "LOAD_ATTR_CLASS",                              183,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_CLASS_WITH_METACLASS_CHECK",         184,    1,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_ATTR_GETATTRIBUTE_OVERRIDDEN",            185,    1,  0,  include_in_dis_has_table=False)
def_op(loc,     "LOAD_ATTR_INSTANCE_VALUE",                     186,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_METHOD_LAZY_DICT",                   187,    1,  2)
def_op(loc,     "LOAD_ATTR_METHOD_NO_DICT",                     188,    1,  2)
def_op(loc,     "LOAD_ATTR_METHOD_WITH_VALUES",                 189,    1,  2)
def_op(loc,     "LOAD_ATTR_MODULE",                             190,    1,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_ATTR_NONDESCRIPTOR_NO_DICT",              191,    1,  1)
def_op(loc,     "LOAD_ATTR_NONDESCRIPTOR_WITH_VALUES",          192,    1,  1)
def_op(loc,     "LOAD_ATTR_PROPERTY",                           193,    1,  0)
def_op(loc,     "LOAD_ATTR_SLOT",                               194,    1,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_ATTR_WITH_HINT",                          195,    1,  1,  include_in_dis_has_table=False)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_GLOBAL_BUILTIN",                          196,    0,  1)  # pushes 1 + (oparg & 1)
def_op(loc,     "LOAD_GLOBAL_MODULE",                           197,    0,  1)  # pushes 1 + (oparg & 1)
name_op(loc,    "LOAD_SUPER_ATTR_ATTR",                         198,    3,  1,  include_in_dis_has_table=False)
name_op(loc,    "LOAD_SUPER_ATTR_METHOD",                       199,    3,  2,  include_in_dis_has_table=False)
def_op(loc,     "RESUME_CHECK",                                 200,    0,  0)
def_op(loc,     "RESUME_CHECK_JIT",                             201,    0,  0)
def_op(loc,     "SEND_ASYNC_GEN",                               202,    3,  3)
def_op(loc,     "SEND_GEN",                                     203,    3,  2)
def_op(loc,     "SEND_VIRTUAL",                                 204,    3,  3)
def_op(loc,     "STORE_ATTR_INSTANCE_VALUE",                    205,    2,  0)
def_op(loc,     "STORE_ATTR_SLOT",                              206,    2,  0)
store_op(loc,   "STORE_ATTR_WITH_HINT",                         207,    2,  0, is_type="name", include_in_dis_has_table=False)
def_op(loc,     "STORE_SUBSCR_DICT",                            208,    3,  0)
def_op(loc,     "STORE_SUBSCR_LIST_INT",                        209,    3,  0)
def_op(loc,     "TO_BOOL_ALWAYS_TRUE",                          210,    1,  1)
def_op(loc,     "TO_BOOL_BOOL",                                 211,    1,  1)
def_op(loc,     "TO_BOOL_INT",                                  212,    1,  1)
def_op(loc,     "TO_BOOL_LIST",                                 213,    1,  1)
def_op(loc,     "TO_BOOL_NONE",                                 214,    1,  1)
def_op(loc,     "TO_BOOL_STR",                                  215,    1,  1)
varargs_op(loc, "UNPACK_SEQUENCE_LIST",                         216,    1,  -1)
varargs_op(loc, "UNPACK_SEQUENCE_TUPLE",                        217,    1,  -1)
def_op(loc,     "UNPACK_SEQUENCE_TWO_TUPLE",                    218,    1,  2)
def_op(loc,     "INSTRUMENTED_END_FOR",                         233,    3,  2)
def_op(loc,     "INSTRUMENTED_POP_ITER",                        234,    1,  0)
def_op(loc,     "INSTRUMENTED_END_SEND",                        235,    2,  1)
jrel_op(loc,    "INSTRUMENTED_FOR_ITER",                        236,    2,  1, conditional=True)
def_op(loc,     "INSTRUMENTED_INSTRUCTION",                     237,    0,  1)
jrel_op(loc,    "INSTRUMENTED_JUMP_FORWARD",                    238,    0,  0, conditional=False, include_in_dis_has_table=False)
def_op(loc,     "INSTRUMENTED_NOT_TAKEN",                       239,    0,  0)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_TRUE",                240,    0,  0, conditional=True, include_in_dis_has_table=False)  # dunno why it's not 1, 0.
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_FALSE",               241,    1,  0, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_NONE",                242,    1,  0, conditional=True, include_in_dis_has_table=False)
jrel_op(loc,    "INSTRUMENTED_POP_JUMP_IF_NOT_NONE",            243,    1,  0, conditional=True, include_in_dis_has_table=False)
def_op(loc,     "INSTRUMENTED_RESUME",                          244,    1,  0)  # dunno why it's not 0, 0.
def_op(loc,     "INSTRUMENTED_RETURN_VALUE",                    245,    1,  1)
def_op(loc,     "INSTRUMENTED_YIELD_VALUE",                     246,    1,  1)
jrel_op(loc,    "INSTRUMENTED_END_ASYNC_FOR",                   247,    0,  0, conditional=True) # dunnow why it's not 2, 0
name_op(loc,    "INSTRUMENTED_LOAD_SUPER_ATTR",                 248,    VARYING_STACK_INT,  1)  # pushes 1 + (oparg & 1)
call_op(loc,    "INSTRUMENTED_CALL",                            249,    -2, 1)
call_op(loc,    "INSTRUMENTED_CALL_KW",                         250,    -3, 1)
call_op(loc,    "INSTRUMENTED_CALL_FUNCTION_EX",                251,    4,  1,  include_in_dis_has_table=False)
jrel_op(loc,    "INSTRUMENTED_JUMP_BACKWARD",                   252,    0,  0, conditional=False, include_in_dis_has_table=False)
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
local_op(loc,   "STORE_FAST_MAYBE_NULL",                        266,    1,  0)


# ops >= 42 have args
HAVE_ARGUMENT = 42

loc["hasarg"] = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 128, 236, 238, 240, 241, 242, 243, 244, 246, 247, 248, 249, 250, 252, 254, 255, 257, 258, 259, 260, 261, 263, 264, 265, 266]
# hasconst table populated by const_op definitions
# hasname table populated by name_op and store_op definitions
# jrel table populated by jrel_op definitions
loc["hasjabs"] = []
loc["hasjump"] = loc["hasjrel"]
# hasfree table populated by free_op and store_op definitions
# haslocal table populated by local_op and store_op definitions
loc["hasexc"] = [263, 264, 265]
loc["hascompare"] = [loc["opmap"]["COMPARE_OP"]]

# fmt: on

### update formatting

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

def format_BINARY_OP_315(arg: int):
    return _nb_ops[arg][1]


def extended_BINARY_OP_315(opc, instructions):
    opname = _nb_ops[instructions[0].argval][1]

    if opname == "%":
        # Make sure to escape % below.
        opname = "%%"

    fmt_str = "%s[%s]" if opname == "[]" else "%s " + opname + " %s"
    return extended_format_binary_op(opc, instructions, fmt_str)


_common_constants = (
    "AssertionError",
    "NotImplementedError",
    "tuple",
    "all",
    "any",
    "list",
    "set",
    "None",        # <--- There is your oparg 7!
    '""',
    "True",
    "False",
    "-1",
    "frozenset",
    "()",
)


def format_LOAD_COMMON_CONSTANT_315(arg: int):
    return _common_constants[arg]


opcode_arg_fmt = opcode_arg_fmt315 = opcode_314.opcode_arg_fmt314.copy()
opcode_arg_fmt315.update(
    {
        "BINARY_OP": format_BINARY_OP_315,
        "LOAD_COMMON_CONSTANT": format_LOAD_COMMON_CONSTANT_315,
    })

opcode_extended_fmt = opcode_extended_fmt315 = opcode_314.opcode_extended_fmt314.copy()
opcode_extended_fmt315.update(
    {
    "BINARY_OP": extended_BINARY_OP_315
    })

# CALL_FUNCTION_EX no longer takes an argument in 3.14/3.15, so it no longer needs to be formatted
opcode_arg_fmt.pop("CALL_FUNCTION_EX", None)

findlinestarts = opcode_314.findlinestarts

update_pj3(globals(), loc)
finalize_opcodes(loc)
