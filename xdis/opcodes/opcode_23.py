# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.3 bytecode opcodes

This is a like Python 2.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import  \
    init_opdata, finalize_opcodes

version = 2.3

l = locals()
init_opdata(l, opcode_2x, version)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    return
updateGlobal()
finalize_opcodes(l)
