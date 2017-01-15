# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.5's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes, init_opdata,
    rm_op)

import xdis.opcodes.opcode_3x as opcode_3x

l = locals()
init_opdata(l, opcode_3x, 3.3)

# Below are opcode changes since Python 3.2

rm_op(l,  'STOP_CODE',   0)
def_op(l, 'YIELD_FROM', 72)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['POP_JUMP_IF_TRUE']})
updateGlobal()

finalize_opcodes(l)

# opcode33.dump_opcodes(opmap)
