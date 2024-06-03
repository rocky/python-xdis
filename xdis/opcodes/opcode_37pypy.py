# (C) Copyright 2021-2024 by Rocky Bernstein
"""
PYPY 3.7 opcodes

This is a like PyPy 3.7's opcode.py with some classification
of stack usage and information for formatting instructions.
"""

import sys
from typing import List

import xdis.opcodes.opcode_37 as opcode_37
from xdis.opcodes.base import (
    call_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    name_op,
    rm_op,
    store_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_36pypy import opcode_arg_fmt36pypy, opcode_extended_fmt36pypy
from xdis.opcodes.opcode_37 import opcode_arg_fmt37, opcode_extended_fmt37

version_tuple = (3, 7)
python_implementation = "PyPy"

# oppush[op] => number of stack entries pushed
oppush: List[int] = [0] * 256

# oppop[op] => number of stack entries popped
oppop: List[int] = [0] * 256

loc = locals()
init_opdata(loc, opcode_37, version_tuple, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# fmt: off
rm_op(loc, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(loc, "LOAD_METHOD",                  160)

call_op(loc, "CALL_FUNCTION_KW",           141, 9, 1)  # #args + (#kwargs << 8)
call_op(loc, "CALL_FUNCTION_EX",           142, -2, 1)

# The following were removed from 3.7 but still in some versions Pypy 3.7

store_op(loc,   'STORE_ANNOTATION',        127, 1, 0, is_type="name")

# PyPy only
# ----------

name_op(loc, "LOOKUP_METHOD",              201, 1, 2)
loc["hasvargs"].append(202)
call_op(loc, "CALL_METHOD_KW",             204, -1, 1)


# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG",     203)

# PyPy 3.6.1 (and 2.7.13) start to introduce LOAD_REVDB_VAR

if sys.version_info[:3] >= (3, 6, 1):
    def_op(loc, "LOAD_REVDB_VAR",          205)


# fmt: on

opcode_arg_fmt = opcode_arg_fmt37pypy = {**opcode_arg_fmt37, **opcode_arg_fmt36pypy}

opcode_extended_fmt = opcode_extended_fmt37pypy = {
    **opcode_extended_fmt37,
    **opcode_extended_fmt36pypy,
}

update_pj3(globals(), loc)
finalize_opcodes(loc)
