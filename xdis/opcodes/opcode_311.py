"""
CPython 3.11 bytecode opcodes

This is a like Python 3.11's opcode.py
"""

import xdis.opcodes.opcode_310 as opcode_310
from xdis.opcodes.base import (
    binary_op,
    def_op,
    extended_format_ATTR,
    extended_format_COMPARE_OP,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_36 import (
    extended_format_CALL_FUNCTION,
    extended_format_CALL_METHOD,
    extended_format_MAKE_FUNCTION,
    format_CALL_FUNCTION_EX,
    format_CALL_FUNCTION_KW,
    format_extended_arg36,
    format_MAKE_FUNCTION,
)
from xdis.opcodes.opcode_37 import extended_format_RAISE_VARARGS, format_RAISE_VARARGS

version_tuple = (3, 11)
python_implementation = "CPython"

loc = l = locals()

init_opdata(l, opcode_310, version_tuple)

# fmt: off
format_value_flags = opcode_310.format_value_flags
## These are removed / replaced since 3.10...
#         OP NAME                 OPCODE
#---------------------------------------
# Binary ops
rm_op(l,  "BINARY_POWER",            19)
rm_op(l,  "BINARY_MULTIPLY",         20)
rm_op(l,  "BINARY_MATRIX_MULTIPLY",  16)
rm_op(l,  "BINARY_FLOOR_DIVIDE",     26)
rm_op(l,  "BINARY_TRUE_DIVIDE",      27)
rm_op(l,  "BINARY_MODULO",           22)
rm_op(l,  "BINARY_ADD",              23)
rm_op(l,  "BINARY_SUBTRACT",         24)
rm_op(l,  "BINARY_LSHIFT",           62)
rm_op(l,  "BINARY_RSHIFT",           63)
rm_op(l,  "BINARY_AND",              64)
rm_op(l,  "BINARY_XOR",              65)
rm_op(l,  "BINARY_OR",               66)
# inplace ops
rm_op(l,  "INPLACE_POWER",           67)
rm_op(l,  "INPLACE_MULTIPLY",        57)
rm_op(l,  "INPLACE_MATRIX_MULTIPLY", 17)
rm_op(l,  "INPLACE_FLOOR_DIVIDE",    28)
rm_op(l,  "INPLACE_TRUE_DIVIDE",     29)
rm_op(l,  "INPLACE_MODULO",          59)
rm_op(l,  "INPLACE_ADD",             55)
rm_op(l,  "INPLACE_SUBTRACT",        56)
rm_op(l,  "INPLACE_LSHIFT",          75)
rm_op(l,  "INPLACE_RSHIFT",          76)
rm_op(l,  "INPLACE_AND",             77)
rm_op(l,  "INPLACE_XOR",             78)
rm_op(l,  "INPLACE_OR",              79)
# call ops
rm_op(l,  "CALL_FUNCTION",          131)
rm_op(l,  "CALL_FUNCTION_KW",       141)
rm_op(l,  "CALL_METHOD",            161)
# DUP and ROT ops
rm_op(l,  "DUP_TOP",                  4)
rm_op(l,  "DUP_TOP_TWO",              5)
rm_op(l,  "ROT_TWO",                  2)
rm_op(l,  "ROT_THREE",                3)
rm_op(l,  "ROT_FOUR",                 6)
rm_op(l,  "ROT_N",                   99)
# exception check and jump
rm_op(l,  "JUMP_IF_NOT_EXC_MATCH",  121)
# jumps
rm_op(l,  "JUMP_ABSOLUTE",          113)
rm_op(l,  "POP_JUMP_IF_FALSE",      114)
rm_op(l,  "POP_JUMP_IF_TRUE",       115)
# setup with
rm_op(l,  "SETUP_WITH",             143)
rm_op(l,  "SETUP_ASYNC_WITH",       154)
# fully removed ops
rm_op(l,  "COPY_DICT_WITHOUT_KEYS",  34)
rm_op(l,  "GEN_START",              129)
rm_op(l,  "POP_BLOCK",               87)
rm_op(l,  "SETUP_FINALLY",          122)
rm_op(l,  "YIELD_FROM",              72)
# match, these two ops had stack effects changed
rm_op(l,  "MATCH_CLASS",            152)
rm_op(l,  "MATCH_KEYS",              33)


# These are added since 3.10...
#          OP NAME                         OPCODE  POP PUSH
#---------------------------------------------------------
# replaced binary and inplace ops
def_op(l, "CACHE",                            0,   0, 0)
binary_op(l, "BINARY_OP",                   122)
# call ops
def_op(l, "CALL",                           171,   1, 0)
def_op(l, "KW_NAMES",                       172,   0, 0)
def_op(l, "PRECALL",                        166,   0, 0)
def_op(l, "PUSH_NULL",                        2,   0, 1)
# replaced DUP and ROT ops
def_op(l, "COPY",                           120,   0, 1)
def_op(l, "SWAP",                            99,   0, 0)
# exception check
def_op(l, "CHECK_EXC_MATCH",                 36,   0, 0)
# jumps, all jumps are now relative jumps
# TODO will likely have to redefine all abs jump ops as reljumps
jrel_op(l, "JUMP_BACKWARD",                 140,   0, 0)
jrel_op(l, "POP_JUMP_BACKWARD_IF_FALSE",    175,   1, 0)
jrel_op(l, "POP_JUMP_BACKWARD_IF_TRUE",     176,   1, 0)
jrel_op(l, "POP_JUMP_BACKWARD_IF_NOT_NONE", 173,   1, 0)
jrel_op(l, "POP_JUMP_BACKWARD_IF_NONE",     174,   1, 0)
jrel_op(l, "POP_JUMP_FORWARD_IF_FALSE",     114,   1, 0)
jrel_op(l, "POP_JUMP_FORWARD_IF_TRUE",      115,   1, 0)
jrel_op(l, "POP_JUMP_FORWARD_IF_NOT_NONE",  128,   1, 0)
jrel_op(l, "POP_JUMP_FORWARD_IF_NONE",      129,   1, 0)
# setup with
def_op(l,  "BEFORE_WITH",                     53,  0, 1)
# match
def_op(l,  "MATCH_CLASS",                    152,  2, 1)
def_op(l,  "MATCH_KEYS",                      33,  0, 1)
# generators and co-routines
def_op(l,  "ASYNC_GEN_WRAP",                  87,  0, 0)
def_op(l,  "RETURN_GENERATOR",                75,  0, 0)
def_op(l,  "SEND",                           123,  0, 0)
# copy free vars for closures
def_op(l,  "COPY_FREE_VARS",                 149,  0, 0)
# new jump
jrel_op(l, "JUMP_BACKWARD_NO_INTERRUPT",    134,   0, 0)
# new create cells op
jrel_op(l, "MAKE_CELL",                     135,   0, 0)
# new exception handling
jrel_op(l, "CHECK_EG_MATCH",                 37,   0, 0)
jrel_op(l, "PREP_RERAISE_STAR",              88,   1, 0)
jrel_op(l, "PUSH_EXC_INFO",                  35,   0, 1)
# resume, acts like a nop
def_op(l, "RESUME",                         151,   0, 0)

## Redefined OPS
rm_op(l, "STORE_DEREF",                     137)
def_op(l, "STORE_DEREF",                    138,   1, 0)

rm_op(l, "LOAD_DEREF",                      136)
def_op(l, "LOAD_DEREF",                     137,   0, 1)

rm_op(l, "DELETE_DEREF",                    138)
def_op(l, "DELETE_DEREF",                   139,   0, 0)

rm_op(l, "GET_AWAITABLE",                    73)
def_op(l, "GET_AWAITABLE",                  131,   0, 0)

rm_op(l, "LOAD_CLOSURE",                    135)
def_op(l, "LOAD_CLOSURE",                   136,   0, 1)

## Update tables
loc["hasconst"].append(172)  # KW_NAMES
loc["hasfree"].extend((135, 136, 137, 138, 139))
loc["hasjabs"] = []

# removed jrel ops 35, 37, 143, 88, 154
loc["hasjrel"] = [93, 110, 111, 112, 114, 115, 123, 128, 129, 134, 140, 173, 174, 175, 176]

# fmt: on
def format_extended_is_op(arg):
    return "is" if arg == 0 else "is not"


def format_extended_contains_op(arg):
    return "in" if arg == 0 else "not in"


opcode_arg_fmt = {
    "CALL_FUNCTION_EX": format_CALL_FUNCTION_EX,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_KW,
    "CONTAINS_OP": format_extended_contains_op,
    "EXTENDED_ARG": format_extended_arg36,
    "FORMAT_VALUE": format_value_flags,
    "IS_OP": format_extended_is_op,
    "MAKE_FUNCTION": format_MAKE_FUNCTION,
    "RAISE_VARARGS": format_RAISE_VARARGS,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "CALL_METHOD": extended_format_CALL_METHOD,
    "COMPARE_OP": extended_format_COMPARE_OP,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
# fmt: on

update_pj3(globals(), l)

finalize_opcodes(l)
