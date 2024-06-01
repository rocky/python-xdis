# (C) Copyright 2016-2017, 2020, 2023 by Rocky Bernstein
"""
CPython 3.2 bytecode opcodes

This is like Python 3.2's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import finalize_opcodes, init_opdata, update_pj3
from xdis.opcodes.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

# FIXME: can we DRY this even more?

version_tuple = (3, 2)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_3x, version_tuple)

# There are no opcodes to add or change because opcode_3x is based on 3.2.
# If there were, they'd be listed below.

opcode_arg_fmt = opcode_arg_fmt32 = opcode_arg_fmt33
opcode_extended_fmt = opcode_extended_fmt32 = opcode_extended_fmt33

update_pj3(globals(), loc)
finalize_opcodes(loc)
