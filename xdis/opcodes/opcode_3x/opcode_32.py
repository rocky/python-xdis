# (C) Copyright 2016-2017, 2020, 2023, 2025 by Rocky Bernstein
"""
CPython 3.2 bytecode opcodes

This is like Python 3.2's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

from xdis.opcodes.base import (
    cpython_implementation,
    def_op,
    finalize_opcodes,
    init_opdata,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_3x.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

from xdis.opcodes.opcode_3x import opcode_33

# FIXME: can we DRY this even more?

python_implementation = cpython_implementation
version_tuple = (3, 2)

loc = locals()

init_opdata(loc, opcode_33, version_tuple)

# fmt: off
#              OP NAME               OPCODE POP PUSH
#--------------------------------------------------
def_op(loc,   "STOP_CODE",                0,  0,  0, fallthrough=False)
rm_op(loc, "YIELD_FROM", 72)

opcode_arg_fmt = opcode_arg_fmt32 = opcode_arg_fmt33
opcode_extended_fmt = opcode_extended_fmt32 = opcode_extended_fmt33

update_pj3(globals(), loc)
finalize_opcodes(loc)
