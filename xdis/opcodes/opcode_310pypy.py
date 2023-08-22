# (C) Copyright 2022-2023 by Rocky Bernstein
"""
PYPY 3.10 opcodes

This is a like PyPy 3.10's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_310 as opcode_310
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_310 import opcode_arg_fmt310, opcode_extended_fmt310

version_tuple = (3, 10)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_310, version_tuple, is_pypy=True)


# fmt: off
rm_op(loc, "ROT_FOUR",    6)
rm_op(loc, "LOAD_METHOD", 160)

# PyPy only
# ----------

name_op(loc, "LOOKUP_METHOD",              201, 1, 2)
loc["hasvargs"].append(202)
nargs_op(loc, "CALL_METHOD_KW",            204, -1, 1)

# Used only in single-mode compilation list-comprehension generators
jrel_op(loc, 'SETUP_EXCEPT',               121,  0,  6, conditional=True)  # ""
varargs_op(loc, "BUILD_LIST_FROM_ARG",     203)
def_op(loc, "LOAD_REVDB_VAR",              205)


# fmt: on

opcode_arg_fmt = opcode_arg_fmt310pypy = opcode_arg_fmt310.copy()
opcode_extended_fmt = opcode_extended_fmt310pypy = opcode_extended_fmt310.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)