# (C) Copyright 2017, 2019-2021 by Rocky Bernstein
"""
CPython 3.0 bytecode opcodes

This is a like Python 3.0's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_CALL_FUNCTION,
    finalize_opcodes,
    format_MAKE_FUNCTION_default_argc,
    format_extended_arg,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj2,
)

import xdis.opcodes.opcode_31 as opcode_31

version = 3.0
version_tuple = (3, 0)
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_31, version_tuple)

# These are in Python 3.x but not in Python 3.0

# fmt: off
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

#          OP NAME            OPCODE POP PUSH
#--------------------------------------------

def_op(l, 'SET_ADD',              17,  2, 0)  # Calls set.add(TOS1[-i], TOS).
                                             # Used to implement set comprehensions.
def_op(l, 'LIST_APPEND',          18,  2, 0)  # Calls list.append(TOS1, TOS).
                                             # Used to implement list comprehensions.
jrel_op(l, 'JUMP_IF_FALSE',      111,  1, 1)
jrel_op(l, 'JUMP_IF_TRUE',       112,  1, 1)
# fmt: on

# Yes, pj2 not pj3 - Python 3.0 is more like 2.7 here with its
# JUMP_IF rather than POP_JUMP_IF.
update_pj2(globals(), l)

opcode_arg_fmt = {
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,
    "EXTENDED_ARG": format_extended_arg,
}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "STORE_ATTR": extended_format_ATTR,
}
finalize_opcodes(l)
