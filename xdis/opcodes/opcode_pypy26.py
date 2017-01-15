# (C) Copyright 2017 by Rocky Bernstein
"""
CPython PYPY 2.6 bytecode opcodes

This is a like Python 2.6's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_26 as opcode_26
from xdis.opcodes.base import (
    def_op, finalize_opcodes, init_opdata,
    name_op, varargs_op
    )

l = locals()
init_opdata(l, opcode_26, 2.6)

# PyPy only
# ----------
name_op(l, 'LOOKUP_METHOD',          201,  1, 2)
def_op(l,  'CALL_METHOD',            202, -1, 1)
l['hasnargs'].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(l, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
def_op(l, 'JUMP_IF_NOT_DEBUG',       204)

# FIXME remove (fix uncompyle6)
opcode_26.updateGlobal()

finalize_opcodes(l)
