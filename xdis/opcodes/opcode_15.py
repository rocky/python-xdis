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
"""
CPython 1.5 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

# These are used from outside this module
from xdis.cross_dis import findlabels, findlinestarts
from xdis.opcodes.base import (  # Although these aren't used here, they are exported
    binary_op,
    compare_op,
    const_op,
    def_op,
    jabs_op,
    jrel_op,
    local_op,
    name_op,
    nargs_op,
    store_op,
    unary_op,
    update_pj2,
    varargs_op,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (1, 5)
python_implementation = "CPython"

cmp_op = (
    "<",
    "<=",
    "==",
    "!=",
    ">",
    ">=",
    "in",
    "not in",
    "is",
    "is not",
    "exception match",
    "BAD",
)

# Opcodes greater than 90 take an instruction operand or "argument"
# as opcode.py likes to call it.
HAVE_ARGUMENT = 90

loc = locals()
loc["python_version"] = version_tuple
loc["cmp_op"] = cmp_op
loc["HAVE_ARGUMENT"] = HAVE_ARGUMENT

# These are just to silence the import above
loc["findlindstarts"] = findlinestarts
loc["findlabels"] = findlabels

# FIXME: can we DRY this even more?

# opcodes that perform a binary operator of the top two stack entries
binaryop = []

hascompare = []
hascondition = []  # conditional operator; has jump offset
hasconst = []
hasfree = []
hasjabs = []
hasjrel = []
haslocal = []
hasname = []
hasnargs = []  # For function-like calls
hasstore = []  # Some sort of store operation
hasvargs = []  # Similar but for operators BUILD_xxx
nofollow = []  # Instruction doesn't fall to the next opcode

# oppush[op] => number of stack entries pushed
# -9 means handle special. Note his forces oppush[i] - oppop[i] negative
oppush = [0] * 256

# oppop[op] => number of stack entries popped
# -1 means handle special.
oppop = [0] * 256

opmap = {}
opname = [""] * 256
for op in range(256):
    opname[op] = "<%r>" % (op,)

# opcodes that perform a unary operation of the top stack entry
unaryop = []

del op

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# fmt: off
def_op(loc, "STOP_CODE", 0, 0, 0, fallthrough=False)
def_op(loc, "POP_TOP", 1)
def_op(loc, "ROT_TWO", 2)
def_op(loc, "ROT_THREE", 3)
def_op(loc, "DUP_TOP", 4)

def_op(loc, "UNARY_POSITIVE",      10)
unary_op(loc, "UNARY_NEGATIVE",    11)
unary_op(loc, "UNARY_NOT",         12)
unary_op(loc, "UNARY_CONVERT",     13)

unary_op(loc, "UNARY_INVERT",      15)

binary_op(loc, "BINARY_POWER",     19)

binary_op(loc, "BINARY_MULTIPLY",  20)
binary_op(loc, "BINARY_DIVIDE",    21)
binary_op(loc, "BINARY_MODULO",    22)
binary_op(loc, "BINARY_ADD",       23)
binary_op(loc, "BINARY_SUBTRACT",  24)
binary_op(loc, "BINARY_SUBSCR",    25)

def_op(loc, "SLICE+0", 30, 1, 1)
def_op(loc, "SLICE+1", 31, 2, 1)
def_op(loc, "SLICE+2", 32, 2, 1)
def_op(loc, "SLICE+3", 33, 3, 1)

store_op(loc,   "STORE_SLICE+0",  40, 2, 0)
store_op(loc,   "STORE_SLICE+1",  41, 3, 0)
store_op(loc,   "STORE_SLICE+2",  42, 3, 0)
store_op(loc,   "STORE_SLICE+3",  43, 4, 0)

def_op(loc,     "DELETE_SLICE+0", 50, 1, 0)
def_op(loc,     "DELETE_SLICE+1", 51, 2, 0)
def_op(loc,     "DELETE_SLICE+2", 52, 2, 0)
def_op(loc,     "DELETE_SLICE+3", 53, 3, 0)

store_op(loc,   "STORE_SUBSCR",   60, 3, 0)  # Implements TOS1[TOS] = TOS2.
def_op(loc,     "DELETE_SUBSCR",  61, 2, 0)  # Implements del TOS1[TOS].

binary_op(loc,  "BINARY_LSHIFT",  62)
binary_op(loc,  "BINARY_RSHIFT",  63)
binary_op(loc,  "BINARY_AND",     64)
binary_op(loc,  "BINARY_XOR",     65)
def_op(loc,     "BINARY_OR",      66)

def_op(loc,     "PRINT_EXPR",     70, 1, 0)
def_op(loc,     "PRINT_ITEM",     71, 1, 0)
def_op(loc,     "PRINT_NEWLINE",  72, 0, 0)

def_op(loc,     "BREAK_LOOP",     80, 0, 0, fallthrough=False)

def_op(loc,     "LOAD_LOCALS",    82, 0, 1)
def_op(loc,     "RETURN_VALUE",   83, 1, 0, fallthrough=False)

def_op(loc,     "EXEC_STMT",      85, 3, 0)

def_op(loc,     "POP_BLOCK",      87, 0, 0)
def_op(loc,     "END_FINALLY",    88, 1, 0)
def_op(loc,     "BUILD_CLASS",    89, 3, 0)

# HAVE_ARGUMENT = 90               # Opcodes from here have an argument:

store_op(loc,   "STORE_NAME",     90, 1, 0, is_type="name")  # Operand is in name list
name_op(loc,    "DELETE_NAME",    91, 0, 0)  # ""
varargs_op(loc, "UNPACK_TUPLE",   92)  # Number of tuple items
def_op(loc,     "UNPACK_LIST",    93)  # Number of list items
store_op(loc,   "STORE_ATTR",     95, 2, 0, is_type="name")  # Operand is in name list
name_op(loc,    "DELETE_ATTR",    96, 1, 0)  # ""
store_op(loc,    "STORE_GLOBAL",  97, 1, 0, is_type="name")  # ""
name_op(loc,    "DELETE_GLOBAL",  98, 0, 0)  # ""

const_op(loc,   "LOAD_CONST",    100, 0, 1)  # Operand is in const list
name_op(loc,    "LOAD_NAME",     101, 0, 1)  # Operand is in name list
varargs_op(loc, "BUILD_TUPLE",   102, -1, 1)  # Number of tuple items
varargs_op(loc, "BUILD_LIST",    103, -1, 1)  # Number of list items
varargs_op(loc, "BUILD_MAP",     104, -1, 1)  # Always zero for now
name_op(loc,    "LOAD_ATTR",     105, 1, 1)  # Operand is in name list
compare_op(loc, "COMPARE_OP",    106, 2, 1)  # Comparison operator

name_op(loc,    "IMPORT_NAME",   107, 2, 1)  # Operand is in name list
name_op(loc,    "IMPORT_FROM",   108, 0, 1)  # Operand is in name list

jrel_op(loc,    "JUMP_FORWARD",  110, 0, 0, fallthrough=False)  # Number of bytes to skip
jrel_op(loc,    "JUMP_IF_FALSE", 111, 1, 1, True)  # ""
jrel_op(loc,    "JUMP_IF_TRUE",  112, 1, 1, True)  # ""
jabs_op(loc,    "JUMP_ABSOLUTE", 113, 0, 0, fallthrough=False)  # Target byte offset from beginning of code
def_op(loc,     "FOR_LOOP",      114)  # Number of bytes to skip

name_op(loc,    "LOAD_GLOBAL",   116, 0, 1)  # Operand is in name list

jrel_op(loc,    "SETUP_LOOP",    120, 0, 0, conditional=True)  # Distance to target address
jrel_op(loc,    "SETUP_EXCEPT",  121, 0, 0)  # ""
jrel_op(loc,    "SETUP_FINALLY", 122, 0, 0)  # ""

local_op(loc, "LOAD_FAST",       124, 0, 1)  # Local variable number
store_op(loc, "STORE_FAST",      125, 1, 0, is_type="local")  # Local variable number
local_op(loc, "DELETE_FAST",     126)  # Local variable number

def_op(loc, "SET_LINENO",        127)  # Current line number

def_op(loc, "RAISE_VARARGS",     130, -1, 0, fallthrough=False)
# Number of raise arguments (1, 2, or 3)
nargs_op(loc, "CALL_FUNCTION",   131, -1, 1)  # #args + (#kwargs << 8)

def_op(loc, "MAKE_FUNCTION",     132, -1, 1)  # Number of args with default values
varargs_op(loc, "BUILD_SLICE",   133, -1, 1)  # Number of items

def_op(loc, "EXTENDED_ARG",      143)

EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()
# fmt: on

update_pj2(globals(), loc)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt_base2x.copy()
