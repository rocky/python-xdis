# (C) Copyright 2017, 2019, 2021, 2023 by Rocky Bernstein
"""
CPython 2.2 bytecode opcodes

This is similar to the opcode portion in Python 2.2's dis.py library.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    update_pj2,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (2, 2)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_2x, version_tuple)

# 2.2 Bytecodes not in 2.3
def_op(loc, "FOR_LOOP", 114)
def_op(loc, "SET_LINENO", 127, 0, 0)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

update_pj2(globals(), loc)
finalize_opcodes(loc)
