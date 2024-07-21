# (C) Copyright 2017-2018, 2020-2021, 2023-2024
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
CPython 3.2 bytecode opcodes to be used as a base for other opcodes including 3.2.

This is used in bytecode disassembly among other things. This is
similar to the opcodes in Python's opcode.py library.

If this file changes the other opcode files may have to be adjusted accordingly.
"""

from typing import Optional, Tuple

from xdis.opcodes.base import (
    binary_op,
    call_op,
    compare_op,
    const_op,
    def_op,
    free_op,
    init_opdata,
    jabs_op,
    jrel_op,
    local_op,
    name_op,
    nargs_op,
    store_op,
    unary_op,
    varargs_op,
)
from xdis.opcodes.format.basic import format_extended_arg
from xdis.opcodes.format.extended import opcode_extended_fmt_base, short_code_repr

loc = locals()
init_opdata(loc, None, None)

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# If the POP field is -1 and the opcode is a var args operation
# then the operand holds the size.
#
# If the POP field is negative and the opcode is a nargs operation
# then pop the operand amount plus the negative of the POP amount.

# fmt: off
#              OP NAME               OPCODE POP PUSH
#--------------------------------------------------
def_op(loc,   "STOP_CODE",                0,  0,  0, fallthrough=False)
def_op(loc,   "POP_TOP",                  1,  1,  0)
def_op(loc,   "ROT_TWO",                  2,  2,  2)
def_op(loc,   "ROT_THREE",                3,  3,  3)
def_op(loc,   "DUP_TOP",                  4,  0,  1)

# Python 3.2+
def_op(loc,   "DUP_TOP_TWO",              5,  0,  2)

def_op(loc,   "NOP",                      9,  0,  0)
unary_op(loc, "UNARY_POSITIVE",          10)
unary_op(loc, "UNARY_NEGATIVE",          11)
unary_op(loc, "UNARY_NOT",               12)

unary_op(loc, "UNARY_INVERT",            15)

binary_op(loc, "BINARY_POWER",           19)
binary_op(loc, "BINARY_MULTIPLY",        20)

binary_op(loc, "BINARY_MODULO",          22)
binary_op(loc, "BINARY_ADD",             23)
binary_op(loc, "BINARY_SUBTRACT",        24)
binary_op(loc, "BINARY_SUBSCR",          25)
binary_op(loc, "BINARY_FLOOR_DIVIDE",    26)
binary_op(loc, "BINARY_TRUE_DIVIDE",     27)
binary_op(loc, "INPLACE_FLOOR_DIVIDE",   28)
binary_op(loc, "INPLACE_TRUE_DIVIDE",    29)

# Gone from Python 3 are Python2's
# SLICE+0 ... SLICE+3
# STORE_SLICE+0 ... STORE_SLICE+3
# DELETE_SLICE+0 ... DELETE_SLICE+3

#          OP NAME                OPCODE POP PUSH
#-----------------------------------------------
store_op(loc, "STORE_MAP",            54,  3,  1)
binary_op(loc, "INPLACE_ADD",            55,  2,  1)
binary_op(loc, "INPLACE_SUBTRACT",       56,  2,  1)
binary_op(loc, "INPLACE_MULTIPLY",       57,  2,  1)

binary_op(loc, "INPLACE_MODULO",         59,  2,  1)
store_op(loc, "STORE_SUBSCR",         60,  3,  0) # Implements TOS1[TOS] = TOS2.
def_op(loc, "DELETE_SUBSCR",          61,  2,  0) # Implements del TOS1[TOS].
binary_op(loc, "BINARY_LSHIFT",       62)
binary_op(loc, "BINARY_RSHIFT",       63)
binary_op(loc, "BINARY_AND",          64)
binary_op(loc, "BINARY_XOR",          65)
binary_op(loc, "BINARY_OR",           66)
binary_op(loc, "INPLACE_POWER",       67)
def_op(loc, "GET_ITER",               68,  1,  1)
store_op(loc, "STORE_LOCALS",         69,  1,  0)

def_op(loc, "PRINT_EXPR",             70,  1,  0)
unary_op(loc, "LOAD_BUILD_CLASS",     71,  0,  1)

# Python3 drops/changes:
#  def_op(loc, "PRINT_ITEM", 71)
#  def_op(loc, "PRINT_NEWLINE", 72)
#  def_op(loc, "PRINT_ITEM_TO", 73)
#  def_op(loc, "PRINT_NEWLINE_TO", 74)

binary_op(loc, "INPLACE_LSHIFT",      75)
binary_op(loc, "INPLACE_RSHIFT",      76)
binary_op(loc, "INPLACE_AND",         77)
binary_op(loc, "INPLACE_XOR",         78)
binary_op(loc, "INPLACE_OR",          79)
def_op(loc, "BREAK_LOOP",             80,  0,  0, fallthrough=False)
def_op(loc, "WITH_CLEANUP",           81,  1,  0) # Cleans up the stack when a with statement
                                                  # block exits.  Handle stack special

def_op(loc, "RETURN_VALUE",           83,  1,  0, fallthrough=False)
def_op(loc, "IMPORT_STAR",            84,  1,  0)

def_op(loc, "YIELD_VALUE",            86,  1,  1)
def_op(loc, "POP_BLOCK",              87,  0,  0)
def_op(loc, "END_FINALLY",            88,  1,  0)
def_op(loc, "POP_EXCEPT",             89,  0,  0)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

#          OP NAME                OPCODE POP PUSH
#-----------------------------------------------
store_op(loc, "STORE_NAME",           90,  1,  0, is_type="name")   # Operand is in name list
name_op(loc, "DELETE_NAME",           91,  0,  0)   # ""
varargs_op(loc, "UNPACK_SEQUENCE",    92,  0, -1)  # unpacks TOS, arg is the count
jrel_op(loc,    "FOR_ITER",           93,  0,  1)

varargs_op(loc, "UNPACK_EX",          94,  0,  0)  # assignment with a starred target; arg is count
store_op(loc, "STORE_ATTR",           95,  2,  0, is_type="name")   # Operand is in name list
name_op(loc, "DELETE_ATTR",           96,  1,  0)   # ""
store_op(loc, "STORE_GLOBAL",         97,  1,  0, is_type="name")   # ""
name_op(loc, "DELETE_GLOBAL",         98,  0,  0)   # ""

# Python 2"s DUP_TOPX is gone starting in Python 3.2

#          OP NAME                OPCODE POP PUSH
#-----------------------------------------------
const_op(loc,   "LOAD_CONST",        100,  0,  1)  # Operand is in const list
loc["nullaryloadop"].add(100)

name_op(loc,    "LOAD_NAME",         101,  0,  1)  # Operand is in name list
loc["nullaryloadop"].add(101)

varargs_op(loc, "BUILD_TUPLE",       102, -1,  1)  # TOS is count of tuple items
varargs_op(loc, "BUILD_LIST",        103, -1,  1)  # TOS is count of list items
varargs_op(loc, "BUILD_SET",         104, -1,  1)  # TOS is count of set items
varargs_op(loc, "BUILD_MAP",         105,  0,  1)  # argument is dictionary count to be pushed
name_op(loc, "LOAD_ATTR",            106,  1,  1)  # Operand is in name list
compare_op(loc, "COMPARE_OP",        107,  2,  1)  # Comparison operator
name_op(loc, "IMPORT_NAME",          108,  2,  1)  # Imports TOS and TOS1; module pushed
loc["nullaryloadop"].add(108)

name_op(loc, "IMPORT_FROM",          109,  0,  1)  # Operand is in name list

jrel_op(loc, "JUMP_FORWARD",         110,  0,  0, fallthrough=False)  # Number of bytes to skip
jabs_op(loc, "JUMP_IF_FALSE_OR_POP", 111, conditional=True)  # Target byte offset from beginning of code
jabs_op(loc, "JUMP_IF_TRUE_OR_POP",  112, conditional=True) # ""
jabs_op(loc, "JUMP_ABSOLUTE",        113,  0,  0, fallthrough=False)  # Target byte offset from beginning of code
jabs_op(loc, "POP_JUMP_IF_FALSE",    114,  2,  1, conditional=True) # ""
jabs_op(loc, "POP_JUMP_IF_TRUE",     115,  2,  1, conditional=True) # ""

name_op(loc, "LOAD_GLOBAL",          116,  0,  1)  # Operand is in name list
loc["nullaryloadop"].add(116)


#          OP NAME                OPCODE POP PUSH
#-----------------------------------------------
jabs_op(loc, "CONTINUE_LOOP",        119,  0,  0, fallthrough=False)  # Target address
jrel_op(loc, "SETUP_LOOP",           120,  0,  0, conditional=True) # Distance to target address
jrel_op(loc, "SETUP_EXCEPT",         121,  0,  6, conditional=True)  # ""
jrel_op(loc, "SETUP_FINALLY",        122,  0,  6, conditional=True)  # ""

local_op(loc, "LOAD_FAST",           124,  0,  1)  # Local variable number
loc["nullaryloadop"].add(124)

store_op(loc, "STORE_FAST",          125,  1,  0, is_type="local")  # Local variable number
local_op(loc, "DELETE_FAST",         126,  0,  0)  # Local variable number

nargs_op(loc, "RAISE_VARARGS",       130, -1,  1, fallthrough=False)
                                                 # Number of raise arguments (1, 2, or 3)

call_op(loc, "CALL_FUNCTION",        131, -1,  1)  # #args + (#kwargs << 8)

nargs_op(loc, "MAKE_FUNCTION",       132, -2,  1) # TOS is number of args if < 3.6
varargs_op(loc, "BUILD_SLICE",       133,  2,  1) # TOS is number of items to pop

nargs_op(loc, "MAKE_CLOSURE",        134, -3,  1) # TOS is number of items to pop
free_op(loc, "LOAD_CLOSURE",         135,  0,  1)
loc["nullaryloadop"].add(135)

loc["nullaryloadop"].add(136)


free_op(loc, "LOAD_DEREF",           136,  0,  1)
loc["nullaryloadop"].add(136)

loc["nullaryop"].add(136)
loc["nullaryloadop"].add(136)

store_op(loc, "STORE_DEREF",         137,  1,  0, is_type="free")
free_op(loc, "DELETE_DEREF",         138,  0,  0)

#          OP NAME                OPCODE POP PUSH
#-----------------------------------------------
nargs_op(loc, "CALL_FUNCTION_VAR",   140,  -2,  1)  # #args + (#kwargs << 8)
nargs_op(loc, "CALL_FUNCTION_KW",    141,  -2,  1)  # #args + (#kwargs << 8)
nargs_op(loc, "CALL_FUNCTION_VAR_KW",142,  -3,  1)   # #args + (#kwargs << 8)

jrel_op(loc, "SETUP_WITH",           143,  0,  7)

def_op(loc, "LIST_APPEND",           145,  2,  1)  # Calls list.append(TOS[-i], TOS).
                                                 # Used to implement list comprehensions.
def_op(loc, "SET_ADD",               146,  1,  0)  # Calls set.add(TOS1[-i], TOS).
                                                 # Used to implement set comprehensions.
def_op(loc, "MAP_ADD",               147,  3,  1)  # Calls dict.setitem(TOS1[-i], TOS, TOS1)
                                                 # Used to implement dict comprehensions.

def_op(loc, "EXTENDED_ARG",          144,  0,   0)
# fmt: on

EXTENDED_ARG = 144

opcode_arg_fmt = {"EXTENDED_ARG": format_extended_arg}


def extended_format_MAKE_FUNCTION_30_35(opc, instructions) -> Tuple[Optional[str], int]:
    """make_function_inst should be a "MAKE_FUNCTION" or "MAKE_CLOSURE" instruction. TOS
    should have the function or closure name.
    """
    # From opcode description: argc indicates the total number of
    # positional and keyword arguments.  Sometimes the function name
    # is in the stack arg positions back.
    assert len(instructions) >= 2
    inst = instructions[0]
    assert inst.opname in ("MAKE_FUNCTION", "MAKE_CLOSURE")
    s = ""
    name_inst = instructions[1]
    start_offset = name_inst.offset
    if name_inst.opname in ("LOAD_CONST",):
        s += f"make_function({short_code_repr(name_inst.argval)}"
        return s, start_offset
    s += format_MAKE_FUNCTION_30_35(inst.argval)
    return s, start_offset


def format_MAKE_FUNCTION_30_35(argc: int) -> str:
    pos_args, name_pair_args, annotate_args = parse_fn_counts_30_35(argc)
    if (pos_args, name_pair_args, annotate_args) == (0, 0, 0):
        return "No arguments"

    s = "%d positional, %d keyword only, %d annotated" % (
        pos_args,
        name_pair_args,
        annotate_args,
    )
    return s


def parse_fn_counts_30_35(argc: int) -> Tuple[int, int, int]:
    """
    In Python 3.0 to 3.5 MAKE_CLOSURE and MAKE_FUNCTION encode
    arguments counts of positional, default + named, and annotation
    arguments a particular kind of encoding where each of
    the entry is a packed byte value of the lower 24 bits
    of ``argc``.  The high bits of argc may have come from
    an EXTENDED_ARG instruction. Here, we unpack the values
    from the ``argc`` int and return a triple of the
    positional args, named_args, and annotation args.
    """
    annotate_count = (argc >> 16) & 0x7FFF
    # For some reason that I don't understand, annotate_args is off by one
    # when there is an EXENDED_ARG instruction from what is documented in
    # https://docs.python.org/3.4/library/dis.html#opcode-MAKE_CLOSURE
    if annotate_count > 1:
        annotate_count -= 1
    return ((argc & 0xFF), (argc >> 8) & 0xFF, annotate_count)


opcode_extended_fmt_base3x = opcode_extended_fmt_base.copy()
