# (C) Copyright 2021, 2023 by Rocky Bernstein
"""
PYPY 3.8 opcodes

This is a like PyPy 3.8's opcode.py  with some classification
of stack usage and information for formatting instructions..
"""

import xdis.opcodes.opcode_38 as opcode_38
from xdis.opcodes.base import (
    call_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    rm_op,
    update_pj3,
    varargs_op,
)
from xdis.opcodes.opcode_37pypy import opcode_arg_fmt37pypy, opcode_extended_fmt37pypy

version_tuple = (3, 8)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_38, version_tuple, is_pypy=True)


# fmt: off
rm_op(loc, "ROT_FOUR",    6)
rm_op(loc, "BUILD_TUPLE_UNPACK_WITH_CALL", 158)
rm_op(loc, "LOAD_METHOD", 160)

# PyPy only
# ----------

name_op(loc, "LOOKUP_METHOD",              201, 1, 2)
loc["hasvargs"].append(202)
call_op(loc, "CALL_METHOD_KW",            204, -1, 1)

# Used only in single-mode compilation list-comprehension generators
jrel_op(loc, 'SETUP_EXCEPT',               121,  0,  6, conditional=True)  # ""
varargs_op(loc, "BUILD_LIST_FROM_ARG",     203)
def_op(loc, "LOAD_REVDB_VAR",              205)


# fmt: on

opcode_arg_fmt = opcode_arg_fmt38pypy = opcode_arg_fmt37pypy.copy()
opcode_extended_fmt = opcode_extended_fmt38pypy = opcode_extended_fmt37pypy.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
