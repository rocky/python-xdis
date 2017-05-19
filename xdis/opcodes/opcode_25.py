# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.5 bytecode opcodes

This is a like Python 2.5's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_24 as opcode_24
from xdis.opcodes.base import (
    def_op, init_opdata,
    finalize_opcodes, format_extended_arg,
    update_pj2)

version = 2.5

l = locals()
init_opdata(l, opcode_24, version)

# Bytecodes added in 2.5 from 2.4
def_op(l, 'WITH_CLEANUP', 81)

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
