# (C) Copyright 2017, 2020-2021 by Rocky Bernstein
"""
CPython 3.1 bytecode opcodes

This is a like Python 3.1's opcode.py with some classification
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
    name_op,
    rm_op,
    update_pj3,
)

import xdis.opcodes.opcode_32 as opcode_32

l = locals()

version = 3.1
version_tuple = (3, 1)
python_implementation = "CPython"

init_opdata(l, opcode_32, version_tuple)

# fmt: off
# These are in Python 3.2 but not in Python 3.1
rm_op(l, "DUP_TOP_TWO",     5)
rm_op(l, "DELETE_DEREF",  138)
rm_op(l, "SETUP_WITH",    143)

# These are in Python 3.1 but not Python 3.2
name_op(l, "IMPORT_NAME", 108,  1, 1)  # Imports TOS and TOS1; module pushed
def_op(l, "ROT_FOUR",       5,  4, 4)
def_op(l, "DUP_TOPX",      99, -1, 2)  # number of items to duplicate

# This op is in 3.2 but its opcode is a 144 instead
def_op(l, "EXTENDED_ARG", 143)
# fmt: on

update_pj3(globals(), l)

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
