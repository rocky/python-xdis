"""
CPython PYPY 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.opcode_2x import findlabels, findlinestarts
from xdis.opcodes.opcode_2x import def_op

# FIXME: can we DRY this even more?

hasArgumentExtended = []

# Make a *copy* of opcode_2x values so we don't pollute 2x

HAVE_ARGUMENT = opcode_2x.HAVE_ARGUMENT
cmp_op = list(opcode_2x.cmp_op)
hasconst = list(opcode_2x.hasconst)
hascompare = list(opcode_2x.hascompare)
hasfree = list(opcode_2x.hasfree)
hasjabs = list(opcode_2x.hasjabs)
hasjrel = list(opcode_2x.hasjrel)
haslocal = list(opcode_2x.haslocal)
hasname = list(opcode_2x.hasname)
hasnargs = list(opcode_2x.hasnargs)
hasvargs = list(opcode_2x.hasvargs)
opmap = deepcopy(opcode_2x.opmap)
opname = deepcopy(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

def updateGlobal():
    globals().update({'python_version': 2.6})

    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update({'JF': opmap['JUMP_FORWARD']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

# Bytecodes added since 2.3.
# 2.4
def_op(opname, opmap, 'NOP', 9)
def_op(opname, opmap, 'LIST_APPEND', 18)
def_op(opname, opmap, 'YIELD_VALUE', 86)

# 2.5
def_op(opname, opmap, 'WITH_CLEANUP', 81)

# 2.6
def_op(opname, opmap, 'STORE_MAP', 54)

def_op(opname, opmap, 'LOOKUP_METHOD', 201)
def_op(opname, opmap, 'CALL_METHOD', 202)
def_op(opname, opmap, 'BUILD_LIST_FROM_ARG', 203)
def_op(opname, opmap, 'JUMP_IF_NOT_DEBUG', 204)

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.6 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
