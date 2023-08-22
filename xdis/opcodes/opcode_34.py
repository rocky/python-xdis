# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_33 as opcode_33
from xdis.opcodes.base import finalize_opcodes, free_op, init_opdata, rm_op, update_pj3
from xdis.opcodes.opcode_33 import opcode_arg_fmt33, opcode_extended_fmt33

version_tuple = (3, 4)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_33, version_tuple)

# fmt: off
# These are removed since Python 3.3
rm_op(loc, "STORE_LOCALS",       69)

# These are new since Python 3.3
free_op(loc, "LOAD_CLASSDEREF", 148)
# fmt: on

opcode_arg_fmt = opcode_arg_fmt34 = opcode_arg_fmt33
opcode_extended_fmt = opcode_extended_fmt34 = opcode_extended_fmt33

update_pj3(globals(), loc)
finalize_opcodes(loc)
