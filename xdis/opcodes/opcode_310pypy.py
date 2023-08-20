# (C) Copyright 2022-2023 by Rocky Bernstein
"""
PYPY 3.10 opcodes

This is a like Python 3.10's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_BINARY_ADD,
    extended_format_BINARY_AND,
    extended_format_BINARY_FLOOR_DIVIDE,
    extended_format_BINARY_MODULO,
    extended_format_BINARY_SUBSCR,
    extended_format_BINARY_SUBTRACT,
    extended_format_COMPARE_OP,
    extended_format_INPLACE_ADD,
    extended_format_INPLACE_FLOOR_DIVIDE,
    extended_format_INPLACE_SUBTRACT,
    extended_format_INPLACE_TRUE_DIVIDE,
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

import xdis.opcodes.opcode_310 as opcode_310
from xdis.opcodes.opcode_36 import extended_format_MAKE_FUNCTION, format_MAKE_FUNCTION

version_tuple = (3, 10)
python_implementation = "PyPy"

l = locals()
init_opdata(l, opcode_310, version_tuple, is_pypy=True)


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
    "BINARY_ADD": extended_format_BINARY_ADD,
    "BINARY_AND": extended_format_BINARY_AND,
    "BINARY_FLOOR_DIVIDE": extended_format_BINARY_FLOOR_DIVIDE,
    "BINARY_MODULO": extended_format_BINARY_MODULO,
    "BINARY_SUBSCR": extended_format_BINARY_SUBSCR,
    "BINARY_SUBTRACT": extended_format_BINARY_SUBTRACT,
    "CALL_METHOD": extended_format_CALL_METHOD,
    "CALL_METHOD_KW": extended_format_CALL_METHOD_KW,
    "COMPARE_OP": extended_format_COMPARE_OP,
    "INPLACE_ADD": extended_format_INPLACE_ADD,
    "INPLACE_FLOOR_DIVIDE": extended_format_INPLACE_FLOOR_DIVIDE,
    "INPLACE_SUBTRACT": extended_format_INPLACE_SUBTRACT,
    "INPLACE_TRUE_DIVIDE": extended_format_INPLACE_TRUE_DIVIDE,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_CLOSURE": extended_format_MAKE_FUNCTION,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

update_pj3(globals(), l)
finalize_opcodes(l)
