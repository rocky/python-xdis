# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.1 bytecode opcodes

This is similar to the opcode portion in Python 2.1's dis.py library.
"""

import xdis.opcodes.opcode_22 as opcode_22
from xdis.opcodes.base import (
    init_opdata, finalize_opcodes, rm_op)

version = 2.1

l = locals()
init_opdata(l, opcode_22, version)

# 2.1 bytecodes changes from 2.2
rm_op(l, 'BINARY_FLOOR_DIVIDE',  26)
rm_op(l, 'BINARY_TRUE_DIVIDE',   27)
rm_op(l, 'INPLACE_FLOOR_DIVIDE', 28)
rm_op(l, 'INPLACE_TRUE_DIVIDE',  29)
rm_op(l, 'GET_ITER', 68)
rm_op(l, 'YIELD_VALUE', 86)
rm_op(l, 'FOR_ITER', 93)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    return

updateGlobal()
finalize_opcodes(l)
