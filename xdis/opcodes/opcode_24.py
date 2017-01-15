# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.4 bytecode opcodes

This is a like Python 2.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op, init_opdata,
    finalize_opcodes)

l = locals()
init_opdata(l, opcode_2x, 2.4)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    return

# Bytecodes added since 2.3
def_op(l, 'NOP',           9,  0,  0)
def_op(l, 'LIST_APPEND',  18,  2,  1)  # Calls list.append(TOS[-i], TOS).
                                       # Used to implement list comprehensions.
def_op(l, 'YIELD_VALUE',  86,  1,  0)

updateGlobal()
finalize_opcodes(l)
