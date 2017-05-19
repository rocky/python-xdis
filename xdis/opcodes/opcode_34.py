# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes,
    format_extended_arg, free_op, init_opdata,
    rm_op, update_pj3)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

import xdis.opcodes.opcode_33 as opcode_33

version = 3.4

l = locals()

init_opdata(l, opcode_33, version)

# These are removed since Python 3.3
rm_op(l, 'STORE_LOCALS', 69)

# These are new since Python 3.3
def_op(l,  'YIELD_FROM',       72)
free_op(l, 'LOAD_CLASSDEREF', 148)

update_pj3(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
