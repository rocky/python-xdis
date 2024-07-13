# (C) Copyright 2018, 2020-2024 by Rocky Bernstein
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

"""CPython core set of bytecode opcodes based on version 2.3

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
    ternary_op,
    unary_op,
    varargs_op,
)
from xdis.opcodes.format.basic import format_MAKE_FUNCTION_10_27, opcode_arg_fmt_base
from xdis.opcodes.format.extended import (
    get_arglist,
    get_instruction_arg,
    opcode_extended_fmt_base,
)

loc = locals()
init_opdata(loc, None, None)

# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

# If the POP field is -1 and the opcode is var args operation
# (hasvargs | hasnargs) operation, then
# the operand holds the size.

# fmt: off
#          OP NAME              OPCODE POP PUSH
#-----------------------------------------------
def_op(loc, "STOP_CODE",               0,  0,  0, fallthrough=False)
def_op(loc, "POP_TOP",                 1,  1,  0)
def_op(loc, "ROT_TWO",                 2,  2,  2)
def_op(loc, "ROT_THREE",               3,  3,  3)
def_op(loc, "DUP_TOP",                 4,  0,  1)
def_op(loc, "ROT_FOUR",                5,  4,  4)

unary_op(loc, "UNARY_POSITIVE",          10)
unary_op(loc, "UNARY_NEGATIVE",          11)
unary_op(loc, "UNARY_NOT",               12)
unary_op(loc, "UNARY_CONVERT",           13)

unary_op(loc, "UNARY_INVERT",            15)

binary_op(loc, "BINARY_POWER",           19)

binary_op(loc, "BINARY_MULTIPLY",        20)
binary_op(loc, "BINARY_DIVIDE",          21)
binary_op(loc, "BINARY_MODULO",          22)
binary_op(loc, "BINARY_ADD",             23)
binary_op(loc, "BINARY_SUBTRACT",        24)
binary_op(loc, "BINARY_SUBSCR",          25)
binary_op(loc, "BINARY_FLOOR_DIVIDE",    26)
binary_op(loc, "BINARY_TRUE_DIVIDE",     27)
binary_op(loc, "INPLACE_FLOOR_DIVIDE",   28)
binary_op(loc, "INPLACE_TRUE_DIVIDE",    29)

unary_op(loc, "SLICE+0",                 30)
binary_op(loc, "SLICE+1",                31)
binary_op(loc, "SLICE+2",                32)
ternary_op(loc, "SLICE+3",               33)

#          OP NAME              OPCODE POP PUSH
#-----------------------------------------------
store_op(loc, "STORE_SLICE+0",        40,  2,  0)
store_op(loc, "STORE_SLICE+1",        41,  3,  0)
store_op(loc, "STORE_SLICE+2",        42,  3,  0)
store_op(loc, "STORE_SLICE+3",        43,  4,  0)

def_op(loc, "DELETE_SLICE+0",         50,  1,  0)
def_op(loc, "DELETE_SLICE+1",         51,  2,  0)
def_op(loc, "DELETE_SLICE+2",         52,  2,  0)
def_op(loc, "DELETE_SLICE+3",         53,  3,  0)

binary_op(loc, "INPLACE_ADD",         55)
binary_op(loc, "INPLACE_SUBTRACT",    56)
binary_op(loc, "INPLACE_MULTIPLY",    57)
binary_op(loc, "INPLACE_DIVIDE",      58)
binary_op(loc, "INPLACE_MODULO",      59)
store_op(loc, "STORE_SUBSCR",         60,  3,  0) # Implements TOS1[TOS] = TOS2.
def_op(loc, "DELETE_SUBSCR",          61,  2,  0) # Implements del TOS1[TOS].

binary_op(loc, "BINARY_LSHIFT",       62)
binary_op(loc, "BINARY_RSHIFT",       63)
binary_op(loc, "BINARY_AND",          64)
binary_op(loc, "BINARY_XOR",          65)
binary_op(loc, "BINARY_OR",           66)
binary_op(loc, "INPLACE_POWER",       67)

def_op(loc, "GET_ITER",               68,  1,  1)

def_op(loc, "PRINT_EXPR",             70,  1,  0)
def_op(loc, "PRINT_ITEM",             71,  1,  0)
def_op(loc, "PRINT_NEWLINE",          72,  0,  0)
def_op(loc, "PRINT_ITEM_TO",          73,  2,  0)
def_op(loc, "PRINT_NEWLINE_TO",       74,  1,  0)
def_op(loc, "INPLACE_LSHIFT",         75,  2,  1)
def_op(loc, "INPLACE_RSHIFT",         76,  2,  1)
def_op(loc, "INPLACE_AND",            77,  2,  1)
def_op(loc, "INPLACE_XOR",            78,  2,  1)
def_op(loc, "INPLACE_OR",             79,  2,  1)
def_op(loc, "BREAK_LOOP",             80,  0,  0, fallthrough=False)

def_op(loc, "LOAD_LOCALS",            82,  0,  1)
def_op(loc, "RETURN_VALUE",           83,  1,  0, fallthrough=False)
def_op(loc, "IMPORT_STAR",            84,  1,  0)
def_op(loc, "EXEC_STMT",              85,  3,  0)
def_op(loc, "YIELD_VALUE",            86,  1,  1)

def_op(loc, "POP_BLOCK",              87,  0,  0)
def_op(loc, "END_FINALLY",            88,  1,  0)
def_op(loc, "BUILD_CLASS",            89,  2,  0)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

#             OP NAME              OPCODE POP PUSH
#-----------------------------------------------
store_op(loc, "STORE_NAME",            90,  1,  0, is_type="name")
                                                    # Operand is in name list
name_op(loc, "DELETE_NAME",            91,  0,  0)  # ""
varargs_op(loc, "UNPACK_SEQUENCE",     92, -1,  1)  # TOS is number of tuple items
jrel_op(loc, "FOR_ITER",               93,  0,  1)  # TOS is read

store_op(loc, "STORE_ATTR",            95,  2,  0, is_type="name")
                                                    # Operand is in name list
name_op(loc, "DELETE_ATTR",            96,  1,  0)  # ""
store_op(loc, "STORE_GLOBAL",          97,  1,  0, is_type="name")  # ""
name_op(loc, "DELETE_GLOBAL",          98,  0,  0)  # ""
nargs_op(loc, "DUP_TOPX",              99, -1,  2)  # number of items to duplicate

const_op(loc, "LOAD_CONST",           100,  0,  1)  # Operand is in const list
loc["nullaryloadop"].add(100)

loc["nullaryloadop"].add(100)

name_op(loc, "LOAD_NAME",             101,  0,  1)  # Operand is in name list
loc["nullaryloadop"].add(101)

varargs_op(loc, "BUILD_TUPLE",        102, -1,  1)  # TOS is number of tuple items
varargs_op(loc, "BUILD_LIST",         103, -1,  1)  # TOS is number of list items
varargs_op(loc, "BUILD_MAP",          104,  0,  1)  # TOS is number of kwarg items.
                                                  # Always zero for now
name_op(loc, "LOAD_ATTR",             105,  1,  1)  # Operand is in name list
compare_op(loc, "COMPARE_OP",         106,  2,  1)  # Comparison operator

name_op(loc, "IMPORT_NAME",           107,  0,  1)  # For < 2.6;  Imports namei; module
                                                    # pushed
name_op(loc, "IMPORT_FROM",           108,  0,  1)  # Operand is in name list

jrel_op(loc, "JUMP_FORWARD",          110,  0,  0, fallthrough=False)
                                                # Number of bytes to skip
jrel_op(loc, "JUMP_IF_FALSE",         111,  1,  1, True)  # ""

jrel_op(loc, "JUMP_IF_TRUE",          112,  1,  1, True)  # ""
jabs_op(loc, "JUMP_ABSOLUTE",         113,  0,  0, fallthrough=False)
                                                # Target byte offset from beginning of
                                                 #code

name_op(loc, "LOAD_GLOBAL",           116,  0,  1)  # Operand is in name list
loc["nullaryloadop"].add(116)


jabs_op(loc, "CONTINUE_LOOP",         119,  0,  0, fallthrough=False)  # Target address
jrel_op(loc, "SETUP_LOOP",            120,  0,  0, conditional=True)  # Distance to
                                                                      # target address
jrel_op(loc, "SETUP_EXCEPT",          121,  0,  3, conditional=True)  # ""
jrel_op(loc, "SETUP_FINALLY",         122,  0,  3, conditional=True)  # ""

local_op(loc, "LOAD_FAST",            124,  0,  1)  # Local variable number
loc["nullaryloadop"].add(124)

store_op(loc, "STORE_FAST",           125,  1,  0, is_type="local")  # Local variable
                                                                     # number
local_op(loc, "DELETE_FAST",          126,  0,  0) # Local variable number is in operand

nargs_op(loc, "RAISE_VARARGS",        130, -1,  2, fallthrough=False)
                                                # Number of raise arguments (1, 2, or 3)
call_op(loc, "CALL_FUNCTION",        131, -1,  2)  # TOS is #args + (#kwargs << 8)

nargs_op(loc, "MAKE_FUNCTION",        132, -1,  2)  # TOS is number of args with
                                                    # default values
varargs_op(loc, "BUILD_SLICE",        133,  2,  1)  # TOS is number of items

def_op(loc, "MAKE_CLOSURE",           134, -3,  1)

free_op(loc, "LOAD_CLOSURE",          135,  0,  1)  # Load of a closured variable
loc["nullaryloadop"].add(135)

free_op(loc, "LOAD_DEREF",            136,  0,  1)
loc["nullaryop"].add(136)
loc["nullaryloadop"].add(136)

store_op(loc, "STORE_DEREF",          137,  1,  0, is_type="free")

call_op(loc, "CALL_FUNCTION_VAR",    140, -2,  1) # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_KW",     141, -2,  1) # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_VAR_KW", 142, -3,  1) # #args + (#kwargs << 8)

def_op(loc, "EXTENDED_ARG", 143)
# fmt: on

EXTENDED_ARG = 143


def extended_format_BUILD_MAP_older(
    opc, instructions: list
) -> Tuple[str, Optional[int]]:
    arg_count = instructions[0].argval
    if arg_count == 0:
        # Note: caller generally handles this when the below isn't right.
        return "{}", instructions[0].offset
    arglist, _, i = get_arglist(instructions, 0, arg_count)
    # from trepan.api import debug; debug()
    if arglist is not None:
        assert isinstance(i, int)
        arg_pairs = [f"{arglist[i]}:{arglist[i+1]}" for i in range(len(arglist), 2)]
        args_str = ", ".join(arg_pairs)
        return "{" + args_str + "}", instructions[i].start_offset
    return "", None


def extended_format_PRINT_ITEM(opc, instructions: list) -> Tuple[str, Optional[int]]:
    instr1 = instructions[1]
    print_arg = get_instruction_arg(instr1)
    return (
        f"print {print_arg},",
        instr1.start_offset,
    )


def extended_format_SLICE_0(opc, instructions: list) -> Tuple[str, Optional[int]]:
    arglist, arg_count, i = get_arglist(instructions, 0, 1)
    if arg_count == 1 and arglist is not None:
        return f"{arglist[0]}[:]", instructions[0].start_offset
    return "", None


def extended_format_SLICE_1(opc, instructions: list) -> Tuple[str, Optional[int]]:
    arglist, arg_count, i = get_arglist(instructions, 0, 2)
    if arg_count == 2 and arglist is not None:
        return f"{arglist[1]}[{arglist[0]}:]", instructions[i].start_offset
    return "", None


def extended_format_SLICE_2(opc, instructions: list) -> Tuple[str, Optional[int]]:
    arglist, arg_count, i = get_arglist(instructions, 0, 2)
    if arg_count == 2 and i is not None and arglist is not None:
        return f"{arglist[1]}[:{arglist[0]}]", instructions[i].start_offset
    return "", None


def extended_format_SLICE_3(opc, instructions: list) -> Tuple[str, Optional[int]]:
    arglist, arg_count, i = get_arglist(instructions, 0, 3)
    if arg_count == 3 and i is not None and arglist is not None:
        arglist = ["" if arg == "None" else arg for arg in arglist]
        return f"{arglist[2]}[{arglist[1]}:{arglist[0]}]", instructions[i].start_offset

    if instructions[0].argval == 0:
        # Degenerate case
        return "set()", instructions[0].start_offset
    return "", None


def format_PRINT_NEWLINE(arg) -> str:
    return 'print "\\n"'


update_arg_fmt_base2x = {
    **opcode_arg_fmt_base,
    **{
        "MAKE_FUNCTION": format_MAKE_FUNCTION_10_27,
        "PRINT_NEWLINE": format_PRINT_NEWLINE,
    },
}

opcode_extended_fmt_base2x = {
    **opcode_extended_fmt_base,
    **{
        # "BUILD_MAP": extended_format_BUILD_MAP_older,
        "PRINT_ITEM": extended_format_PRINT_ITEM,
        "SLICE+0": extended_format_SLICE_0,
        "SLICE+1": extended_format_SLICE_1,
        "SLICE+2": extended_format_SLICE_2,
        "SLICE+3": extended_format_SLICE_3,
    },
}
