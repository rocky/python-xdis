# (C) Copyright 2019-2021 by Rocky Bernstein
"""
PYPY 3.6 opcodes

This is a like Python 3.6's opcode.py with some classification
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
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    varargs_op,
    update_pj3,
)

version = 3.6
version_tuple = (3, 6)
python_implementation = "PyPy"

from xdis.opcodes.opcode_33 import extended_format_MAKE_FUNCTION
import xdis.opcodes.opcode_36 as opcode_36
from xdis.opcodes.opcode_36 import (
    format_MAKE_FUNCTION_flags,
)

l = locals()
init_opdata(l, opcode_36, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# Opcodes removed from 3.6.

rm_op(l, "CALL_FUNCTION_EX", 142)
rm_op(l, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)

# The following were removed from 3.6 but still in Pypy 3.6
def_op(l, "MAKE_CLOSURE", 134, 9, 1)  # TOS is number of items to pop
nargs_op(l, "CALL_FUNCTION_VAR", 140, 9, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_KW", 141, 9, 1)  # #args + (#kwargs << 8)
nargs_op(l, "CALL_FUNCTION_VAR_KW", 142, 9, 1)  # #args + (#kwargs << 8)

# PyPy only
# ----------

name_op(l, "LOOKUP_METHOD", 201, 1, 2)
nargs_op(l, "CALL_METHOD", 202, -1, 1)
l["hasvargs"].append(202)


# Used only in single-mode compilation list-comprehension generators
varargs_op(l, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(l, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR
import sys

if sys.version_info[:3] >= (3, 6, 1):
    def_op(l, "LOAD_REVDB_VAR", 205)

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

opcode_arg_fmt = {
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_flags,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

finalize_opcodes(l)
