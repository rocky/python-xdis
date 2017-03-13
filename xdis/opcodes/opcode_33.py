# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes, init_opdata,
    rm_op, update_pj3)

import xdis.opcodes.opcode_3x as opcode_3x

version = 3.3

l = locals()
init_opdata(l, opcode_3x, version)

# Below are opcode changes since Python 3.2

rm_op(l,  'STOP_CODE',   0)
def_op(l, 'YIELD_FROM', 72)

update_pj3(globals(), l)

finalize_opcodes(l)
