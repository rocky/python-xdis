# (C) Copyright 2017, 2019-2021, 2023-2024 by Rocky Bernstein
"""
CPython 3.0 bytecode opcodes

This is a like Python 3.0's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_31 as opcode_31
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj2,
)
from xdis.opcodes.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

version_tuple = (3, 0)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_31, version_tuple)

# These are in Python 3.x but not in Python 3.0

# fmt: off
rm_op(loc, "JUMP_IF_FALSE_OR_POP", 111)
rm_op(loc, "JUMP_IF_TRUE_OR_POP",  112)
rm_op(loc, "POP_JUMP_IF_FALSE",    114)
rm_op(loc, "POP_JUMP_IF_TRUE",     115)
rm_op(loc, "LIST_APPEND",          145)
rm_op(loc, "SET_ADD",              146)
rm_op(loc, "MAP_ADD",              147)

# These are are in 3.0 but are not in 3.1 or they have
# different opcode numbers. Note: As a result of opcode value
# changes, these have to be applied *after* removing ops (with
# the same name).

#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
def_op(loc, "SET_ADD",              17,  2, 0)  # Calls set.add(TOS1[-i], TOS).
                                             # Used to implement set comprehensions.
def_op(loc, "LIST_APPEND",          18,  2, 0)  # Calls list.append(TOS1, TOS).
                                             # Used to implement list comprehensions.
jrel_op(loc, "JUMP_IF_FALSE",      111,  1, 1)
jrel_op(loc, "JUMP_IF_TRUE",       112,  1, 1)

# fmt: on

# Yes, pj2 not pj3 - Python 3.0 is more like 2.7 here with its
# JUMP_IF rather than POP_JUMP_IF.

opcode_arg_fmt = opcode_arg_fmt31 = opcode_arg_fmt33
opcode_extended_fmt = opcode_extended_fmt31 = opcode_extended_fmt33

update_pj2(globals(), loc)
finalize_opcodes(loc)
