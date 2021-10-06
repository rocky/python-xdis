# (C) Copyright 2019-2021 by Rocky Bernstein
"""
PYPY 3.3 opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import (
    extended_format_ATTR,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    varargs_op,
    update_pj3,
)

version = 3.3
version_tuple = (3, 3)
python_implementation = "PyPy"

import xdis.opcodes.opcode_33 as opcode_33

l = locals()
init_opdata(l, opcode_33, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(l, "LOOKUP_METHOD", 201, 1, 2)
nargs_op(l, "CALL_METHOD", 202, -1, 1)
l["hasvargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(l, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(l, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

finalize_opcodes(l)

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
