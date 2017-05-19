# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.0 bytecode opcodes

This is a like Python 3.0's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op, finalize_opcodes, format_extended_arg, init_opdata,
    jrel_op, rm_op, update_pj2)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

import xdis.opcodes.opcode_31 as opcode_31

version = 3.0

l = locals()

init_opdata(l, opcode_31, version)

# These are in Python 3.x but not in Python 3.0

rm_op(l, 'JUMP_IF_FALSE_OR_POP', 111)
rm_op(l, 'JUMP_IF_TRUE_OR_POP',  112)
rm_op(l, 'POP_JUMP_IF_FALSE',    114)
rm_op(l, 'POP_JUMP_IF_TRUE',     115)
rm_op(l, 'LIST_APPEND',          145)
rm_op(l, 'MAP_ADD',              147)

# These are are in 3.0 but are not in 3.1 or they have
# different opcode numbers. Note: As a result of opcode value
# changes, these have to be applied *after* removing ops (with
# the same name).

def_op(l, 'SET_ADD',        17,  1, 0)
def_op(l, 'LIST_APPEND',    18,  2, 1)

jrel_op(l, 'JUMP_IF_FALSE', 111, 1, 1)
jrel_op(l, 'JUMP_IF_TRUE',  112, 1, 1)

# This op is in 3.x but its opcode is a 144 instead
def_op(l, 'EXTENDED_ARG',  143)

update_pj2(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
