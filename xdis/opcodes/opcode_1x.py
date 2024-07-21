# (C) Copyright 2017, 2019-2021, 2023 by Rocky Bernstein
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
"""CPython core set of bytecode opcodes based on version 1.5

This is used in bytecode disassembly among other things. This is
similar to the opcodes in Python's opcode.py library.

If this file changes the other opcode files may have to be adjusted accordingly.
"""

from xdis.opcodes.base import (
    binary_op,
    call_op,
    compare_op,
    const_op,
    def_op,
    init_opdata,
    jabs_op,
    jrel_op,
    local_op,
    name_op,
    store_op,
    ternary_op,
    unary_op,
    update_pj2,
    varargs_op,
)
from xdis.opcodes.format.basic import format_MAKE_FUNCTION_10_27, opcode_arg_fmt_base
from xdis.opcodes.format.extended import opcode_extended_fmt_base
from xdis.opcodes.opcode_2x import (
    extended_format_PRINT_ITEM,
    extended_format_SLICE_0,
    extended_format_SLICE_1,
    extended_format_SLICE_2,
    extended_format_SLICE_3,
)

loc = locals()
init_opdata(loc, None, None)

# Opcodes greater than 90 take an instruction operand or "argument"
# as opcode.py likes to call it.
HAVE_ARGUMENT = 90


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# If the POP field is -1 and the opcode is var args operation
# (hasvargs | hasnargs) operation, then
# the operand holds the size.

# fmt: off

#                OP NAME        OPCODE POP PUSH
#-----------------------------------------------
def_op(loc,   "STOP_CODE",           0,  0,  0, fallthrough=False)
def_op(loc,   "POP_TOP",             1)
def_op(loc,   "ROT_TWO",             2)
def_op(loc,   "ROT_THREE",           3)
def_op(loc,   "DUP_TOP",             4)

def_op(loc,     "UNARY_POSITIVE",   10)
unary_op(loc,   "UNARY_NEGATIVE",   11)
unary_op(loc,   "UNARY_NOT",        12)
unary_op(loc,   "UNARY_CONVERT",    13)

unary_op(loc,   "UNARY_INVERT",     15)

binary_op(loc,  "BINARY_POWER",     19)

binary_op(loc,  "BINARY_MULTIPLY",  20)
binary_op(loc,  "BINARY_DIVIDE",    21)
binary_op(loc,  "BINARY_MODULO",    22)
binary_op(loc,  "BINARY_ADD",       23)
binary_op(loc,  "BINARY_SUBTRACT",  24)
binary_op(loc,  "BINARY_SUBSCR",    25)

unary_op(loc, "SLICE+0",            30)
binary_op(loc, "SLICE+1",           31)
binary_op(loc, "SLICE+2",           32)
ternary_op(loc, "SLICE+3",          33)

#          OP NAME              OPCODE POP PUSH
#-----------------------------------------------
store_op(loc,   "STORE_SLICE+0",    40, 2, 0)
store_op(loc,   "STORE_SLICE+1",    41, 3, 0)
store_op(loc,   "STORE_SLICE+2",    42, 3, 0)
store_op(loc,   "STORE_SLICE+3",    43, 4, 0)

def_op(loc,     "DELETE_SLICE+0",   50, 1, 0)
def_op(loc,     "DELETE_SLICE+1",   51, 2, 0)
def_op(loc,     "DELETE_SLICE+2",   52, 2, 0)
def_op(loc,     "DELETE_SLICE+3",   53, 3, 0)

store_op(loc,   "STORE_SUBSCR",     60, 3, 0)  # Implements TOS1[TOS] = TOS2.
def_op(loc,     "DELETE_SUBSCR",    61, 2, 0)  # Implements del TOS1[TOS].

binary_op(loc,  "BINARY_LSHIFT",    62)
binary_op(loc,  "BINARY_RSHIFT",    63)
binary_op(loc,  "BINARY_AND",       64)
binary_op(loc,  "BINARY_XOR",       65)
def_op(loc,     "BINARY_OR",        66)

def_op(loc,     "PRINT_EXPR",       70, 1, 0)
def_op(loc,     "PRINT_ITEM",       71, 1, 0)
def_op(loc,     "PRINT_NEWLINE",    72, 0, 0)

def_op(loc,     "BREAK_LOOP",       80, 0, 0, fallthrough=False)

def_op(loc,     "LOAD_LOCALS",      82, 0, 1)
def_op(loc,     "RETURN_VALUE",     83, 1, 0, fallthrough=False)

def_op(loc,     "EXEC_STMT",        85, 3, 0)

def_op(loc,     "POP_BLOCK",        87, 0, 0)
def_op(loc,     "END_FINALLY",      88, 1, 0)
def_op(loc,     "BUILD_CLASS",      89, 3, 0)

# HAVE_ARGUMENT = 90               # Opcodes from here have an argument:

#                OP NAME        OPCODE POP PUSH
#-----------------------------------------------
store_op(loc,   "STORE_NAME",       90, 1, 0, is_type="name")  # Operand is in name list
name_op(loc,    "DELETE_NAME",      91, 0, 0)  # ""
varargs_op(loc, "UNPACK_TUPLE",     92)  # Number of tuple items
def_op(loc,     "UNPACK_LIST",      93)  # Number of list items
store_op(loc,   "STORE_ATTR",       95, 2, 0, is_type="name")  # Operand is in name list
name_op(loc,    "DELETE_ATTR",      96, 1, 0)  # ""
store_op(loc,    "STORE_GLOBAL",    97, 1, 0, is_type="name")  # ""
name_op(loc,    "DELETE_GLOBAL",    98, 0, 0)  # ""

const_op(loc,   "LOAD_CONST",      100, 0, 1)  # Operand is in const list
loc["nullaryloadop"].add(100)

name_op(loc,    "LOAD_NAME",       101, 0, 1)  # Operand is in name list
loc["nullaryloadop"].add(101)

varargs_op(loc, "BUILD_TUPLE",     102, -1, 1)  # Number of tuple items
varargs_op(loc, "BUILD_LIST",      103, -1, 1)  # Number of list items
varargs_op(loc, "BUILD_MAP",       104, -1, 1)  # Always zero for now
name_op(loc,    "LOAD_ATTR",       105, 1, 1)  # Operand is in name list
compare_op(loc, "COMPARE_OP",      106, 2, 1)  # Comparison operator

name_op(loc,    "IMPORT_NAME",   107, 2, 1)  # Operand is in name list
loc["nullaryloadop"].add(107)

name_op(loc,    "IMPORT_FROM",   108, 0, 1)  # Operand is in name list

jrel_op(loc,    "JUMP_FORWARD",  110, 0, 0, fallthrough=False)  # Number of bytes to skip
jrel_op(loc,    "JUMP_IF_FALSE", 111, 1, 1, True)  # ""
jrel_op(loc,    "JUMP_IF_TRUE",  112, 1, 1, True)  # ""
jabs_op(loc,    "JUMP_ABSOLUTE", 113, 0, 0, fallthrough=False)
                                             # Target byte offset from beginning of code
def_op(loc,     "FOR_LOOP",      114)  # Number of bytes to skip

name_op(loc,    "LOAD_GLOBAL",   116, 0, 1)  # Operand is in name list
loc["nullaryloadop"].add(116)

jrel_op(loc,    "SETUP_LOOP",    120, 0, 0, conditional=True)
                                             # Distance to target address
jrel_op(loc,    "SETUP_EXCEPT",  121, 0, 0)  # ""
jrel_op(loc,    "SETUP_FINALLY", 122, 0, 0)  # ""

local_op(loc, "LOAD_FAST",       124, 0, 1)  # Local variable number
loc["nullaryloadop"].add(124)

store_op(loc, "STORE_FAST",      125, 1, 0, is_type="local")  # Local variable number
local_op(loc, "DELETE_FAST",     126)  # Local variable number

def_op(loc, "SET_LINENO",        127)  # Current line number

def_op(loc, "RAISE_VARARGS",     130, -1, 0, fallthrough=False)
# Number of raise arguments (1, 2, or 3)
call_op(loc, "CALL_FUNCTION",   131, -1, 1)  # #args + (#kwargs << 8)

def_op(loc, "MAKE_FUNCTION",     132, -1, 1)  # Number of args with default values
varargs_op(loc, "BUILD_SLICE",   133, -1, 1)  # Number of items

def_op(loc, "EXTENDED_ARG",      143)

EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()
# fmt: on

update_pj2(globals(), loc)

update_arg_fmt_base1x = {
    **opcode_arg_fmt_base,
    **{
        "MAKE_FUNCTION": format_MAKE_FUNCTION_10_27,
    },
}

opcode_extended_fmt_base1x = {
    **opcode_extended_fmt_base,
    **{
        "PRINT_ITEM": extended_format_PRINT_ITEM,
        "SLICE+0": extended_format_SLICE_0,
        "SLICE+1": extended_format_SLICE_1,
        "SLICE+2": extended_format_SLICE_2,
        "SLICE+3": extended_format_SLICE_3,
    },
}
