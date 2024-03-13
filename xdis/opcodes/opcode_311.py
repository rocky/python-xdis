# (C) Copyright 2024
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

from copy import copy

import xdis.opcodes.opcode_310 as opcode_310
from xdis.opcodes.base import (
    binary_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.format.extended import extended_format_binary_op
from xdis.opcodes.opcode_310 import opcode_arg_fmt310, opcode_extended_fmt310

version_tuple = (3, 11)
python_implementation = "CPython"

oppush = []
oppop = []
opmap = {}

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
def_op(loc, "LOAD_CLOSURE",                   136,   0, 1)
def_op(loc, "LOAD_DEREF",                     137,   0, 1)
def_op(loc, "STORE_DEREF",                    138,   1, 0)
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


def extended_format_BINARY_OP(opc, instructions):
    opname = _nb_ops[instructions[0].argval][1]
    if opname == "%":
        opname = "%%"
    return extended_format_binary_op(opc, instructions, "%%s %s %%s" % opname)


def format_BINARY_OP(arg):
    return _nb_ops[arg][1]


opcode_arg_fmt311 = copy(opcode_arg_fmt310)
del opcode_arg_fmt311["CALL_FUNCTION"]
del opcode_arg_fmt311["CALL_FUNCTION_KW"]
del opcode_arg_fmt311["CALL_METHOD"]

opcode_arg_fmt = opcode_arg_fmt311 = copy(opcode_arg_fmt310)
opcode_arg_fmt.update(
    {
        "BINARY_OP": format_BINARY_OP,
    }
)

opcode_extended_fmt311 = copy(opcode_extended_fmt310)
opcode_extended_fmt311.update(
    {
        "BINARY_OP": extended_format_BINARY_OP,
    },
)

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

opcode_extended_fmt = opcode_extended_fmt311

update_pj3(globals(), loc)
finalize_opcodes(loc)


def parse_location_entries(location_bytes, first_line):
    """
    Parses the locations table described in: https://github.com/python/cpython/blob/3.11/Objects/locations.md
    The locations table replaced the line number table starting in 3.11
    """

    def starts_new_entry(b):
        return bool(b & int("0b10000000", 2))  # bit 7 is set

    def extract_code(b):
        return (b & int("0b01111000", 2)) >> 3  # extracts bits 3-6

    def extract_length(b):
        return (b & int("0b00000111", 2)) + 1  # extracts bit 0-2

    def iter_location_codes(loc_bytes):
        if len(loc_bytes) == 0:
            return []

        result = []
        iter_locs = iter(loc_bytes)
        entry_codes = [next(iter_locs)]
        result.append(entry_codes)

        for b in iter_locs:
            if starts_new_entry(b):
                result.append(entry_codes)
                entry_codes = [b]
            else:
                entry_codes.append(b)

        return result

    def iter_varints(varint_bytes):
        if len(varint_bytes) == 0:
            return []

        def has_next_byte(b):
            return bool(b & int("0b01000000", 2))  # has bit 6 set

        def get_value(b):
            return b & int("0b00111111", 2)  # extracts bits 0-5

        iter_varint_bytes = iter(varint_bytes)

        current_value = 0
        shift_amt = 0

        result = []
        for b in iter_varint_bytes:
            current_value += get_value(b) << shift_amt
            if has_next_byte(b):
                shift_amt += 6
            else:
                result.append(current_value)
                current_value = 0
                shift_amt = 0
        return result

    def decode_signed_varint(s):
        if s & 1:
            return -(s >> 1)
        else:
            return s >> 1

    entries = (
        []
    )  # tuples of (code units, start line, end line, start column, end column)

    last_line = first_line

    for location_codes in iter_location_codes(location_bytes):
        first_byte = location_codes[0]
        location_length = extract_length(first_byte)
        code = extract_code(first_byte)

        if code <= 9:  # short form
            start_line = last_line
            end_line = start_line
            second_byte = location_codes[1]
            start_column = (code * 8) + ((second_byte >> 4) & 7)
            end_column = start_column + (second_byte & 15)
        elif code <= 12:  # one line form
            start_line = last_line + code - 10
            end_line = start_line
            start_column = location_codes[1]
            end_column = location_codes[2]
        elif code == 13:  # no column info
            (start_line_delta,) = iter_varints(location_codes[1:])
            start_line = last_line + decode_signed_varint(start_line_delta)
            end_line = start_line
            start_column = None
            end_column = None
        elif code == 14:  # long form
            (start_line_delta, end_line_delta, start_column, end_column) = iter_varints(
                location_codes[1:]
            )
            start_line = last_line + decode_signed_varint(start_line_delta)
            end_line = start_line + end_line_delta
        else:  # code == 15, no location
            start_line = None
            end_line = None
            start_column = None
            end_column = None

        entries.append(
            (location_length, start_line, end_line, start_column, end_column)
        )

        if start_line is not None:
            last_line = start_line

    return entries


from xdis.cross_dis import findlinestarts  # noqa

opcode_arg_fmt = opcode_arg_fmt311 = opcode_arg_fmt310.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
