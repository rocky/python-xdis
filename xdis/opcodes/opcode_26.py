# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.6 bytecode opcodes

This is a like Python 2.6's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes, format_extended_arg,
    init_opdata, update_pj2)
import xdis.opcodes.opcode_25 as opcode_25

version = 2.6

l = locals()
init_opdata(l, opcode_25, version)

# Below are opcode changes since Python 2.5
def_op(l, 'STORE_MAP', 54, 3, 1)

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
