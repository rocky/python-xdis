# (C) Copyright 2017, 2020, 2023-2024 by Rocky Bernstein
"""
PYPY 3.5 opcodes

This is a like Python 3.5's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_35 as opcode_35
from xdis.opcodes.base import (
    call_op,
    def_op,
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
from xdis.opcodes.opcode_36 import extended_format_BUILD_STRING

version_tuple = (3, 5)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_35, version_tuple, is_pypy=True)

## FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
def_op(loc, "FORMAT_VALUE", 155)
varargs_op(loc, "BUILD_STRING", 157)
name_op(loc, "LOOKUP_METHOD", 201, 1, 2)
call_op(loc, "CALL_METHOD", 202, -1, 1)
loc["hasvargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

# Python 3.5.3 PyPYy 7.0.0 adds LOAD_REVDB.  We can't distinguish
# between the two kinds of bytecode by Python version number, or magic
# number. And we don't have a means of specifying
# platform.python_branch() which would give us the 7.0.0 as opposed to
# 6.0.0.

# Lacking anything better to do, we'll add this opcode since
# the newest PyPy for 3.5 has it.

def_op(loc, "LOAD_REVDB_VAR", 205)

opcode_extended_fmt = {
    "BUILD_STRING": extended_format_BUILD_STRING,
    "CALL_METHOD": extended_format_CALL_METHOD,
    "LOAD_ATTR": extended_format_ATTR,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

# FIXME remove (fix uncompyle6)
update_pj3(globals(), loc)
finalize_opcodes(loc)
