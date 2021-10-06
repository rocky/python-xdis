# (C) Copyright 2021 by Rocky Bernstein
"""
PYPY 3.7 opcodes

This is a like Python 3.7's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    format_CALL_FUNCTION_pos_name_encoded,
    def_op,
    extended_format_ATTR,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_RAISE_VARARGS_older,
    format_extended_arg,
    init_opdata,
    name_op,
    nargs_op,
    rm_op,
    store_op,
    varargs_op,
    update_pj3,
)

version = 3.7
version_tuple = (3, 7)
python_implementation = "PyPy"

from xdis.opcodes.opcode_33 import extended_format_MAKE_FUNCTION
import xdis.opcodes.opcode_37 as opcode_37
from xdis.opcodes.opcode_37 import (
    format_MAKE_FUNCTION_flags,
)

l = locals()
init_opdata(l, opcode_37, version_tuple, is_pypy=True)


# FIXME: DRY common PYPY opcode additions

# fmt: off
rm_op(l, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(l, "LOAD_METHOD",                  160)

nargs_op(l, "CALL_FUNCTION_KW",          141, 9, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_EX",          142, -2, 1)

# The following were removed from 3.7 but still in Pypy 3.7

store_op(l,   'STORE_ANNOTATION',        127, 1, 0, is_type="name")

# PyPy only
# ----------

name_op(l, "LOOKUP_METHOD",              201, 1, 2)
l["hasvargs"].append(202)
nargs_op(l, "CALL_METHOD_KW",            204, -1, 1)


# Used only in single-mode compilation list-comprehension generators
varargs_op(l, "BUILD_LIST_FROM_ARG",     203)

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR
import sys

if sys.version_info[:3] >= (3, 6, 1):
    def_op(l, "LOAD_REVDB_VAR",          205)

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

opcode_arg_fmt = {
    "EXTENDED_ARG":  format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_flags,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
    'CALL_FUNCTION': format_CALL_FUNCTION_pos_name_encoded,
}

opcode_extended_fmt = {
    "LOAD_ATTR":     extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE":  extended_format_RETURN_VALUE,
    "STORE_ATTR":    extended_format_ATTR,
}
# Fmtxblackn: on

finalize_opcodes(l)
