# (C) Copyright 2019-2021, 2023-2024 by Rocky Bernstein
"""
PYPY 3.3 opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_33 as opcode_33
from xdis.opcodes.base import (
    call_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.format.extended import (
    extended_format_ATTR,
    extended_format_CALL_METHOD,
    extended_format_RETURN_VALUE,
)

version_tuple = (3, 3)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_33, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(loc, "LOOKUP_METHOD", 201, 1, 2)
call_op(loc, "CALL_METHOD", 202, -1, 1)
loc["hasvargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

# FIXME remove (fix uncompyle6)
opcode_extended_fmt = {
    "CALL_METHOD": extended_format_CALL_METHOD,
    "LOAD_ATTR": extended_format_ATTR,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

update_pj3(globals(), loc)
finalize_opcodes(loc)
