"""
CPython PYPY 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_26 as opcode_26
from xdis.opcodes.base import cmp_op, def_op, name_op, varargs_op
# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_2x values so we don't pollute 2x

HAVE_ARGUMENT = opcode_26.HAVE_ARGUMENT
cmp_op        = list(cmp_op)
hasconst      = list(opcode_26.hasconst)
hascompare    = list(opcode_26.hascompare)
hasfree       = list(opcode_26.hasfree)
hasjabs       = list(opcode_26.hasjabs)
hasjrel       = list(opcode_26.hasjrel)
haslocal      = list(opcode_26.haslocal)
hasname       = list(opcode_26.hasname)
hasnargs      = list(opcode_26.hasnargs)
hasvargs      = list(opcode_26.hasvargs)
opmap         = deepcopy(opcode_26.opmap)
opname        = deepcopy(opcode_26.opname)
EXTENDED_ARG  = opcode_26.EXTENDED_ARG

# PyPy only
# ----------
name_op(l, 'LOOKUP_METHOD',          201,  1, 2)
def_op(l,  'CALL_METHOD',            202, -1, 1)
hasnargs.append(202)
varargs_op(l, 'BUILD_LIST_FROM_ARG', 203)
def_op(l, 'JUMP_IF_NOT_DEBUG',       204)

opcode_26.updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.6 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
