# (C) Copyright 2025 by Rocky Bernstein
"""
PYPY 3.11 opcodes

This is a like Python's 3.10's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

import xdis.opcodes.opcode_310 as opcode_310
from xdis.opcodes.base import (
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    nargs_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_311 import opcode_arg_fmt311, opcode_extended_fmt311

version_tuple = (3, 11)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_310, version_tuple, is_pypy=True)


# fmt: off
# Changed opcodes
# ----------------------

# Removed from Python 3.10
# ----------------

rm_op(loc,  "GEN_START",              129)
rm_op(loc,  "LIST_EXTEND",            162)
rm_op(loc,  "SET_UPDATE",             163)
rm_op(loc,  "DICT_MERGE",             164)
rm_op(loc,  "DICT_UPDATE",            165)

# Added in PyPy 3.11
# --------------------

def_op(loc, "CHECK_EG_MATCH",                  37,   0, 0)
jrel_op(loc, "PREP_RERAISE_STAR",              88,   1, 0)
def_op(loc, "LIST_EXTEND",                    164,   1, 1)
def_op(loc, "SET_UPDATE",                     165,   2, 1)
def_op(loc, "DICT_MERGE",                     166,   2, 1)
def_op(loc, "DICT_UPDATE",                    167,   2, 1)

loc["hasvargs"].append(202)
nargs_op(loc, "CALL_METHOD_KW",            204, -1, 1)

# Used only in single-mode compilation list-comprehension generators
jrel_op(loc, 'SETUP_EXCEPT',               120,  0,  6, conditional=True)  # ""
varargs_op(loc, "BUILD_LIST_FROM_ARG",     203)
def_op(loc, "LOAD_REVDB_VAR",              205)


# fmt: on

opcode_arg_fmt = opcode_arg_fmt311pypy = opcode_arg_fmt311.copy()
opcode_extended_fmt = opcode_extended_fmt311pypy = opcode_extended_fmt311.copy()

update_pj3(globals(), loc, True)
finalize_opcodes(loc)
