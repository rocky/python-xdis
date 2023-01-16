# (C) Copyright 2022-2023 by Rocky Bernstein
"""
PYPY 3.9 opcodes

This is a like Python 3.8's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_extended_arg,
    format_RAISE_VARARGS_older,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_37pypy import (
    extended_format_CALL_METHOD,
    extended_format_CALL_METHOD_KW,
    format_CALL_METHOD,
    format_CALL_METHOD_KW,
)

version = 3.9
version_tuple = (3, 9)
python_implementation = "PyPy"

import xdis.opcodes.opcode_39 as opcode_39
from xdis.opcodes.opcode_36 import extended_format_MAKE_FUNCTION, format_MAKE_FUNCTION

l = locals()
init_opdata(l, opcode_39, version_tuple, is_pypy=True)


# fmt: off
rm_op(l, "ROT_FOUR",    6)
rm_op(l, "LOAD_METHOD", 160)

# PyPy only
# ----------

name_op(l, "LOOKUP_METHOD",              201, 1, 2)
l["hasvargs"].append(202)
nargs_op(l, "CALL_METHOD_KW",            204, -1, 1)

# Used only in single-mode compilation list-comprehension generators
jrel_op(l, 'SETUP_EXCEPT',               121,  0,  6, conditional=True)  # ""
varargs_op(l, "BUILD_LIST_FROM_ARG",     203)
def_op(l, "LOAD_REVDB_VAR",              205)


# fmt: on
opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_METHOD": format_CALL_METHOD,
    "CALL_METHOD_KW": format_CALL_METHOD_KW,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_CLOSURE": format_MAKE_FUNCTION,
    "MAKE_FUNCTION": format_MAKE_FUNCTION,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_METHOD": extended_format_CALL_METHOD,
    "CALL_METHOD_KW": extended_format_CALL_METHOD_KW,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_CLOSURE": extended_format_MAKE_FUNCTION,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

update_pj3(globals(), l)
finalize_opcodes(l)
