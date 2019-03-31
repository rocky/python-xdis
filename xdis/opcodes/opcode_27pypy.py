# (C) Copyright 2017 by Rocky Bernstein
"""
PYPY 2.7 opcodes

This is a like Python 2.7's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_27 as opcode_27
from xdis.opcodes.base import (
    def_op, finalize_opcodes, init_opdata,
    jrel_op, name_op, nargs_op, update_pj3
    )

version = 2.7

l = locals()

init_opdata(l, opcode_27, version, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(l,    'LOOKUP_METHOD',   201,  1, 2)
nargs_op(l, 'CALL_METHOD',     202, -1, 1)
l['hasnargs'].append(202)

# Used only in single-mode compilation list-comprehension generators
def_op(l, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
jrel_op(l, 'JUMP_IF_NOT_DEBUG',  204, conditional=True)


# PyPy 2.7.13 (and 3.6.1) start to introduce LOAD_REVDB_VAR
import sys
if sys.version_info[:3] >= (2, 7, 13) and sys.version_info[4] >= 42:
    def_op(l, 'LOAD_REVDB_VAR', 205)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

# FIXME remove (fix uncompyle6)
update_pj3(globals(), l)

finalize_opcodes(l)
