# (C) Copyright 2024-2025
# by Rocky Bernstein
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
CPython 3.11 bytecode opcodes

This is like Python 3.11's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

from typing import Dict, List, Optional, Tuple

import xdis.opcodes.opcode_310 as opcode_310
from xdis.instruction import Instruction
from xdis.opcodes.base import (
    binary_op,
    def_op,
    finalize_opcodes,
    free_op,
    init_opdata,
    jrel_op,
    rm_op,
    store_op,
    update_pj3,
)
from xdis.opcodes.format.extended import (
    NULL_EXTENDED_OP,
    extended_format_binary_op,
    extended_format_unary_op,
)
from xdis.opcodes.opcode_310 import opcode_arg_fmt310, opcode_extended_fmt310

version_tuple = (3, 11)
python_implementation = "CPython"

# oppush[op] => number of stack entries pushed
oppush: List[int] = [0] * 256

# oppop[op] => number of stack entries popped
oppop: List[int] = [0] * 256

# opmap[opcode_name] => opcode_number
opmap: Dict[str, int] = {}

_nb_ops = [
    ("NB_ADD", "+"),
    ("NB_AND", "&"),
    ("NB_FLOOR_DIVIDE", "//"),
    ("NB_LSHIFT", "<<"),
    ("NB_MATRIX_MULTIPLY", "@"),
    ("NB_MULTIPLY", "*"),
    ("NB_MODULO", "%"),
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
    ("NB_INPLACE_MODULO", "%="),
    ("NB_INPLACE_OR", "|="),
    ("NB_INPLACE_POWER", "**="),
    ("NB_INPLACE_RSHIFT", ">>="),
    ("NB_INPLACE_SUBTRACT", "-="),
    ("NB_INPLACE_TRUE_DIVIDE", "/="),
    ("NB_INPLACE_XOR", "^="),
]


loc = locals()

init_opdata(loc, opcode_310, version_tuple)

# fmt: off
## These are removed / replaced since 3.10...
#         OP NAME                 OPCODE
#---------------------------------------
# Binary ops
rm_op(loc,  "BINARY_POWER",            19)
rm_op(loc,  "BINARY_MULTIPLY",         20)
rm_op(loc,  "BINARY_MATRIX_MULTIPLY",  16)
rm_op(loc,  "BINARY_FLOOR_DIVIDE",     26)
rm_op(loc,  "BINARY_TRUE_DIVIDE",      27)
rm_op(loc,  "BINARY_MODULO",           22)
rm_op(loc,  "BINARY_ADD",              23)
rm_op(loc,  "BINARY_SUBTRACT",         24)
rm_op(loc,  "BINARY_LSHIFT",           62)
rm_op(loc,  "BINARY_RSHIFT",           63)
rm_op(loc,  "BINARY_AND",              64)
rm_op(loc,  "BINARY_XOR",              65)
rm_op(loc,  "BINARY_OR",               66)
# inplace ops
rm_op(loc,  "INPLACE_POWER",           67)
rm_op(loc,  "INPLACE_MULTIPLY",        57)
rm_op(loc,  "INPLACE_MATRIX_MULTIPLY", 17)
rm_op(loc,  "INPLACE_FLOOR_DIVIDE",    28)
rm_op(loc,  "INPLACE_TRUE_DIVIDE",     29)
rm_op(loc,  "INPLACE_MODULO",          59)
rm_op(loc,  "INPLACE_ADD",             55)
rm_op(loc,  "INPLACE_SUBTRACT",        56)
rm_op(loc,  "INPLACE_LSHIFT",          75)
rm_op(loc,  "INPLACE_RSHIFT",          76)
rm_op(loc,  "INPLACE_AND",             77)
rm_op(loc,  "INPLACE_XOR",             78)
rm_op(loc,  "INPLACE_OR",              79)
# call ops
rm_op(loc,  "CALL_FUNCTION",          131)
rm_op(loc,  "CALL_FUNCTION_KW",       141)
rm_op(loc,  "CALL_METHOD",            161)
# DUP and ROT ops
rm_op(loc,  "DUP_TOP",                  4)
rm_op(loc,  "DUP_TOP_TWO",              5)
rm_op(loc,  "ROT_TWO",                  2)
rm_op(loc,  "ROT_THREE",                3)
rm_op(loc,  "ROT_FOUR",                 6)
rm_op(loc,  "ROT_N",                   99)
# exception check and jump
rm_op(loc,  "JUMP_IF_NOT_EXC_MATCH",  121)
# jumps
rm_op(loc,  "JUMP_ABSOLUTE",          113)
rm_op(loc,  "POP_JUMP_IF_FALSE",      114)
rm_op(loc,  "POP_JUMP_IF_TRUE",       115)
# setup with
rm_op(loc,  "SETUP_WITH",             143)
rm_op(loc,  "SETUP_ASYNC_WITH",       154)
# fully removed ops
rm_op(loc,  "COPY_DICT_WITHOUT_KEYS",  34)
rm_op(loc,  "GEN_START",              129)
rm_op(loc,  "POP_BLOCK",               87)
rm_op(loc,  "SETUP_FINALLY",          122)
rm_op(loc,  "YIELD_FROM",              72)
# match, these two ops had stack effects changed
rm_op(loc,  "MATCH_CLASS",            152)
rm_op(loc,  "MATCH_KEYS",              33)

## Redefined OPS

# We to redefine 138 from DELETE_REF to STORE_DEREF.
# So we have to rm DELETE_DEREF with opcode 138 *before* adding
# STORE_DEREF with opcode 138.

rm_op(loc, "GET_AWAITABLE",                    73)
rm_op(loc, "LOAD_CLOSURE",                    135)
rm_op(loc, "LOAD_DEREF",                      136)
rm_op(loc, "STORE_DEREF",                     137)
rm_op(loc, "DELETE_DEREF",                    138)

## Redefined OPS
def_op(loc, "GET_AWAITABLE",                  131,   0, 0)
free_op(loc, "LOAD_CLOSURE",                  136,   0, 1)
loc["nullaryloadop"].add(136)

free_op(loc, "LOAD_DEREF",                    137,   0, 1)
loc["nullaryop"].add(137)
loc["nullaryloadop"].add(137)

store_op(loc, "STORE_DEREF",                  138,   1, 0, is_type="free")
def_op(loc, "DELETE_DEREF",                   139,   0, 0)

# These are added since 3.10...
#          OP NAME                         OPCODE  POP PUSH
#---------------------------------------------------------
# replaced binary and inplace ops
def_op(loc, "CACHE",                            0,   0, 0)
binary_op(loc, "BINARY_OP",                   122)
# call ops
def_op(loc, "CALL",                           171,   1, 0)
def_op(loc, "KW_NAMES",                       172,   0, 0)
def_op(loc, "PRECALL",                        166, 100, 0)
def_op(loc, "PUSH_NULL",                        2,   0, 1)
# replaced DUP and ROT ops
def_op(loc, "COPY",                           120,   0, 1)
def_op(loc, "SWAP",                            99,   0, 0)
# exception check
def_op(loc, "CHECK_EXC_MATCH",                 36,   0, 0)
# jumps, all jumps are now relative jumps
# TODO will likely have to redefine all abs jump ops as reljumps
jrel_op(loc, "JUMP_BACKWARD",                 140,   0, 0)
jrel_op(loc, "POP_JUMP_BACKWARD_IF_FALSE",    175,   1, 0)
jrel_op(loc, "POP_JUMP_BACKWARD_IF_TRUE",     176,   1, 0)
jrel_op(loc, "POP_JUMP_BACKWARD_IF_NOT_NONE", 173,   1, 0)
jrel_op(loc, "POP_JUMP_BACKWARD_IF_NONE",     174,   1, 0)
jrel_op(loc, "POP_JUMP_FORWARD_IF_FALSE",     114,   1, 0)
jrel_op(loc, "POP_JUMP_FORWARD_IF_TRUE",      115,   1, 0)
jrel_op(loc, "POP_JUMP_FORWARD_IF_NOT_NONE",  128,   1, 0)
jrel_op(loc, "POP_JUMP_FORWARD_IF_NONE",      129,   1, 0)
# setup with
def_op(loc,  "BEFORE_WITH",                     53,  0, 1)
# match
def_op(loc,  "MATCH_CLASS",                    152,  3, 1)
def_op(loc,  "MATCH_KEYS",                      33,  0, 1)
# generators and co-routines
def_op(loc,  "ASYNC_GEN_WRAP",                  87,  0, 0)
def_op(loc,  "RETURN_GENERATOR",                75,  0, 0)
def_op(loc,  "SEND",                           123,  0, 0)
# copy free vars for closures
def_op(loc,  "COPY_FREE_VARS",                 149,  0, 0)
# new jump
jrel_op(loc, "JUMP_BACKWARD_NO_INTERRUPT",    134,   0, 0)
# new create cells op
jrel_op(loc, "MAKE_CELL",                     135,   0, 0)
# new exception handling
jrel_op(loc, "CHECK_EG_MATCH",                 37,   0, 0)
jrel_op(loc, "PREP_RERAISE_STAR",              88,   1, 0)
jrel_op(loc, "PUSH_EXC_INFO",                  35,   0, 1)
# resume, acts like a nop
def_op(loc, "RESUME",                         151,   0, 0)

## Update tables
# removed jrel ops 35, 37, 143, 88, 154

loc["hasconst"].append(172)  # KW_NAMES
loc["hasfree"].extend((135, 136, 137, 138, 139))
loc["hasjabs"] = []
loc["hasjrel"] = [
    93, 110, 111, 112, 114, 115, 123, 128, 129, 134, 140, 173, 174, 175,
    176]

# Changed stack effects
oppop[opmap["POP_EXCEPT"]] = 1
oppop[opmap["END_ASYNC_FOR"]] = 2
oppop[opmap["RERAISE"]] = 1

# fmt: on


def extended_format_BINARY_OP(opc, instructions) -> Tuple[str, Optional[int]]:
    opname = _nb_ops[instructions[0].argval][1]
    if opname == "%":
        opname = "%%"
    elif opname == "%=":
        opname = "%%="
    return extended_format_binary_op(opc, instructions, f"%s {opname} %s")


def extended_format_COPY_OP(
    opc, instructions: List[Instruction]
) -> Tuple[str, Optional[int]]:
    """Try to extract TOS value and show that surrounded in a "push() ".
    The trailing space at the used as a sentinal for `get_instruction_tos_str()`
    which tries to remove the push() part when the operand value string is needed.
    """

    # We add a space at the end as a sentinal to use in get_instruction_tos_str()
    if instructions[1].optype not in ["jrel", "jabs"]:
        return extended_format_unary_op(opc, instructions, "copy(%s) ")
    else:
        return NULL_EXTENDED_OP


def extended_format_SWAP(
    opc, instructions: List[Instruction]
) -> Tuple[str, Optional[int]]:
    """call_function_inst should be a "SWAP" instruction. See if
    `we can find the two instructions to be swapped.  If not we'll
    return None.

    """
    # From opcode description: argc indicates the total number of
    # positional and keyword arguments.  Sometimes the function name
    # is in the stack arg positions back.
    # From opcode description: arg_count indicates the total number of
    # positional and keyword arguments.

    swap_instr = instructions[0]
    i = swap_instr.argval
    # s = ""

    if i is None or not (0 < i < len(instructions)):
        return "", None

    # To be continued
    return "", None


def format_BINARY_OP(arg: int) -> str:
    return _nb_ops[arg][1]


def format_SWAP_OP(arg: int) -> str:
    return f"TOS <-> TOS{arg-1}"


opcode_arg_fmt311 = opcode_arg_fmt310.copy()
del opcode_arg_fmt311["CALL_FUNCTION"]
del opcode_arg_fmt311["CALL_FUNCTION_KW"]
del opcode_arg_fmt311["CALL_METHOD"]

opcode_arg_fmt = opcode_arg_fmt311 = {
    **opcode_arg_fmt310,
    **{
        "BINARY_OP": format_BINARY_OP,
        "SWAP": format_SWAP_OP,
    },
}

opcode_extended_fmt = opcode_extended_fmt311 = {
    **opcode_extended_fmt310,
    **{
        "BINARY_OP": extended_format_BINARY_OP,
        "COPY": extended_format_COPY_OP,
    },
}

del opcode_extended_fmt311["BINARY_ADD"]
del opcode_extended_fmt311["BINARY_AND"]
del opcode_extended_fmt311["BINARY_FLOOR_DIVIDE"]
del opcode_extended_fmt311["BINARY_LSHIFT"]
del opcode_extended_fmt311["BINARY_MATRIX_MULTIPLY"]
del opcode_extended_fmt311["BINARY_MODULO"]
del opcode_extended_fmt311["BINARY_MULTIPLY"]
del opcode_extended_fmt311["BINARY_OR"]
del opcode_extended_fmt311["BINARY_POWER"]
del opcode_extended_fmt311["BINARY_RSHIFT"]
del opcode_extended_fmt311["BINARY_SUBTRACT"]
del opcode_extended_fmt311["BINARY_TRUE_DIVIDE"]
del opcode_extended_fmt311["BINARY_XOR"]
del opcode_extended_fmt311["CALL_FUNCTION"]
del opcode_extended_fmt311["CALL_FUNCTION_KW"]
# del opcode_extended_fmt311["CALL_METHOD"]
del opcode_extended_fmt311["INPLACE_ADD"]
del opcode_extended_fmt311["INPLACE_AND"]
del opcode_extended_fmt311["INPLACE_FLOOR_DIVIDE"]
del opcode_extended_fmt311["INPLACE_LSHIFT"]
del opcode_extended_fmt311["INPLACE_MATRIX_MULTIPLY"]
del opcode_extended_fmt311["INPLACE_MODULO"]
del opcode_extended_fmt311["INPLACE_MULTIPLY"]
del opcode_extended_fmt311["INPLACE_OR"]
del opcode_extended_fmt311["INPLACE_POWER"]
del opcode_extended_fmt311["INPLACE_RSHIFT"]
del opcode_extended_fmt311["INPLACE_SUBTRACT"]
del opcode_extended_fmt311["INPLACE_TRUE_DIVIDE"]
del opcode_extended_fmt311["INPLACE_XOR"]

from xdis.opcodes.opcode_310 import findlinestarts

update_pj3(globals(), loc)
finalize_opcodes(loc)
