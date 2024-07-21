# (C) Copyright 2017, 2020-2021, 2023-2024 by Rocky Bernstein
"""
CPython 3.1 bytecode opcodes

This is a like Python 3.1's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_32 as opcode_32
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    name_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

loc = locals()

version_tuple = (3, 1)
python_implementation = "CPython"

init_opdata(loc, opcode_32, version_tuple)

# fmt: off
# These are in Python 3.2 but not in Python 3.1
rm_op(loc, "DUP_TOP_TWO",     5)
rm_op(loc, "DELETE_DEREF",  138)
rm_op(loc, "SETUP_WITH",    143)
rm_op(loc, "EXTENDED_ARG",  144)

# These are in Python 3.1 but not Python 3.2
name_op(loc, "IMPORT_NAME", 108,  1, 1)  # Imports TOS and TOS1; module pushed
loc["nullaryloadop"].add(108)

def_op(loc, "ROT_FOUR",       5,  4, 4)
def_op(loc, "DUP_TOPX",      99, -1, 2)  # number of items to duplicate

# This op is in 3.2 but its opcode is a 144 instead
def_op(loc, "EXTENDED_ARG", 143)
# fmt: on

opcode_arg_fmt = opcode_arg_fmt31 = opcode_arg_fmt33.copy()
opcode_extended_fmt = opcode_extended_fmt31 = opcode_extended_fmt33.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
