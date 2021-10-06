# (C) Copyright 2016-2017, 2020 by Rocky Bernstein
"""
CPython 3.2 bytecode opcodes

This is a like Python 3.2's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_CALL_FUNCTION,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_MAKE_FUNCTION_default_argc,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    update_pj3,
)

# FIXME: can we DRY this even more?

version = 3.2
version_tuple = (3, 2)
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_3x, version_tuple)

# There are no opcodes to add or change.
# If there were, they'd be listed below.

update_pj3(globals(), l)

opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

finalize_opcodes(l)
