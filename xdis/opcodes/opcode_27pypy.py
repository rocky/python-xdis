# (C) Copyright 2017, 2020, 2023 by Rocky Bernstein
"""
PYPY 2.7 opcodes

This is a like Python 2.7's opcode.py with some classification
of stack usage.
"""
import sys
import xdis.opcodes.opcode_27 as opcode_27
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    update_pj3,
)

from xdis.opcodes.opcode_2x import update_arg_fmt_base2x, opcode_extended_fmt_base2x

version_tuple = (2, 7)
python_implementation = "PyPy"

loc = locals()

init_opdata(loc, opcode_27, version_tuple, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(loc, "LOOKUP_METHOD", 201, 1, 2)
nargs_op(loc, "CALL_METHOD", 202, -1, 1)
loc["hasnargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
def_op(loc, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)


# PyPy 2.7.13 (and 3.6.1) start to introduce LOAD_REVDB_VAR

if sys.version_info[:3] >= (2, 7, 13) and sys.version_info[4] >= 42:
    def_op(loc, "LOAD_REVDB_VAR", 205)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

# FIXME remove (fix uncompyle6)
update_pj3(globals(), loc)
finalize_opcodes(loc)
