# (C) Copyright 2017, 2020-2021 by Rocky Bernstein
"""
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_CALL_FUNCTION,
    extended_format_RAISE_VARARGS_older,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    free_op,
    init_opdata,
    rm_op,
    update_pj3,
)

import xdis.opcodes.opcode_33 as opcode_33

version = 3.4
version_tuple = (3, 4)
python_implementation = "CPython"

l = locals()

init_opdata(l, opcode_33, version_tuple)

# fmt: off
# These are removed since Python 3.3
rm_op(l, "STORE_LOCALS",       69)

# These are new since Python 3.3
free_op(l, "LOAD_CLASSDEREF", 148)
# fmt: on

update_pj3(globals(), l)

opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "MAKE_FUNCTION": opcode_33.format_MAKE_FUNCTION_default_pos_arg,
    "EXTENDED_ARG": format_extended_arg,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": opcode_33.extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "STORE_ATTR": extended_format_ATTR,
}

finalize_opcodes(l)
