# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.4 bytecode opcodes

This is a like Python 2.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op, init_opdata,
    finalize_opcodes, format_extended_arg, update_pj2)

version = 2.4

l = locals()
init_opdata(l, opcode_2x, version)

# Bytecodes added since 2.3
def_op(l, 'NOP',           9,  0,  0)
def_op(l, 'LIST_APPEND',  18,  2,  1)  # Calls list.append(TOS[-i], TOS).
                                       # Used to implement list comprehensions.
def_op(l, 'YIELD_VALUE',  86,  1,  0)

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
