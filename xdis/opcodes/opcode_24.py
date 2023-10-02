# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 2.4 bytecode opcodes

This is a like Python 2.3's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    update_pj2,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (2, 4)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_2x, version_tuple)

# fmt: off
# Bytecodes added since 2.3
#          OP NAME            OPCODE POP PUSH
 # Used to implement list comprehensions.
def_op(loc, 'YIELD_VALUE',          86,  1,  1)
# --------------------------------------------
def_op(loc, "NOP", 9, 0, 0)
def_op(loc, "LIST_APPEND", 18, 2, 0)  # Calls list.append(TOS[-i], TOS).
# Used to implement list comprehensions.
def_op(loc, "YIELD_VALUE", 86, 1, 1)

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

# FIXME remove (fix uncompyle6)
update_pj2(globals(), loc)
finalize_opcodes(loc)

# fmt: on
