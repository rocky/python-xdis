# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.2 bytecode opcodes

This is similar to the opcode portion in Python 2.2's dis.py library.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op, init_opdata, finalize_opcodes)

version = 2.2

l = locals()
init_opdata(l, opcode_2x, version)

# 2.2 Bytecodes not in 2.3
def_op(l, 'FOR_LOOP',   114)
def_op(l, 'SET_LINENO', 127, 0, 0)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    return
updateGlobal()
finalize_opcodes(l)
