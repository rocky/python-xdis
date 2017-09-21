# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes,
    format_extended_arg, init_opdata,
    rm_op, update_pj3)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

import xdis.opcodes.opcode_3x as opcode_3x

version = 3.3

l = locals()
init_opdata(l, opcode_3x, version)

# Below are opcode changes since Python 3.2

rm_op(l,  'STOP_CODE',   0)
def_op(l, 'YIELD_FROM', 72, 1, 0)

update_pj3(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
