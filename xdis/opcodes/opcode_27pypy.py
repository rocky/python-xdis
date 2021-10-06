# (C) Copyright 2017, 2020 by Rocky Bernstein
"""
PYPY 2.7 opcodes

This is a like Python 2.7's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_27 as opcode_27
from xdis.opcodes.base import (
    def_op,
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
    jrel_op,
    name_op,
    nargs_op,
    update_pj3,
)

version = 2.7
version_tuple = (2, 7)
python_implementation = "PyPy"

l = locals()

init_opdata(l, opcode_27, version_tuple, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(l, "LOOKUP_METHOD", 201, 1, 2)
nargs_op(l, "CALL_METHOD", 202, -1, 1)
l["hasnargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
def_op(l, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(l, "JUMP_IF_NOT_DEBUG", 204, conditional=True)


# PyPy 2.7.13 (and 3.6.1) start to introduce LOAD_REVDB_VAR
import sys

if sys.version_info[:3] >= (2, 7, 13) and sys.version_info[4] >= 42:
    def_op(l, "LOAD_REVDB_VAR", 205)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

opcode_arg_fmt = {
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,
    "EXTENDED_ARG": format_extended_arg,
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

finalize_opcodes(l)

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
