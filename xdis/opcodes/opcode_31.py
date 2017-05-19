# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.1 bytecode opcodes

This is a like Python 3.1's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, format_extended_arg, finalize_opcodes, init_opdata,
    rm_op, update_pj3)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

import xdis.opcodes.opcode_32 as opcode_32

l = locals()

version = 3.1

init_opdata(l, opcode_32, version)

# These are in Python 3.2 but not in Python 3.1
rm_op(l, 'DUP_TOP_TWO',    5)
rm_op(l, 'DELETE_DEREF', 138)
rm_op(l, 'SETUP_WITH',   143)

# These are in Python 3.1 but not Python 3.2
def_op(l, 'ROT_FOUR', 5)
def_op(l, 'DUP_TOPX', 99)

# This op is in 3.2 but its opcode is a 144 instead
def_op(l, 'EXTENDED_ARG', 143)

update_pj3(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
