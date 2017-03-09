"""
CPython 2.0 bytecode opcodes

This is similar to the opcode portion in Python 2.0's dis.py library.
"""

import xdis.opcodes.opcode_21 as opcode_21
from xdis.opcodes.base import (
    init_opdata, finalize_opcodes, rm_op)

version = 2.0

l = locals()
init_opdata(l, opcode_21, version)

# 2.1 Bytecodes not in 2.0
rm_op(l, 'CONTINUE_LOOP', 119)
rm_op(l, 'MAKE_CLOSURE',  134)
rm_op(l, 'LOAD_CLOSURE',  135)
rm_op(l, 'LOAD_DEREF',    136)
rm_op(l, 'STORE_DEREF',   137)

# FIXME remove (fix uncompyle6)
def updateGlobal():
    globals().update({'PJIF': l['opmap']['JUMP_IF_FALSE']})
    globals().update({'PJIT': l['opmap']['JUMP_IF_TRUE']})
    return

updateGlobal()
finalize_opcodes(l)
