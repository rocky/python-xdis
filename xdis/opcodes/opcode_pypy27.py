"""
CPython PYPY 2.7 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_27 as opcode_27
from xdis.opcodes.opcode_2x import def_op, rm_op

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_2x values so we don't pollute 2x

HAVE_ARGUMENT = opcode_27.HAVE_ARGUMENT
cmp_op        = list(opcode_27.cmp_op)
hasconst      = list(opcode_27.hasconst)
hascompare    = list(opcode_27.hascompare)
hasfree       = list(opcode_27.hasfree)
hasjabs       = list(opcode_27.hasjabs)
hasjrel       = list(opcode_27.hasjrel)
haslocal      = list(opcode_27.haslocal)
hasname       = list(opcode_27.hasname)
hasnargs      = list(opcode_27.hasnargs)
hasvargs      = list(opcode_27.hasvargs)
opmap         = deepcopy(opcode_27.opmap)
opname        = deepcopy(opcode_27.opname)
EXTENDED_ARG  = opcode_27.EXTENDED_ARG

def updateGlobal(version):
    globals().update({'python_version': version})

    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

def jrel_op(name, op, pop=-2, push=-2):
    def_op(opname, opmap, name, op, pop, push)
    hasjrel.append(op)

def jabs_op(name, op, pop=-2, push=-2):
    def_op(opname, opmap, name, op, pop, push)
    hasjabs.append(op)

def name_op(opname, opmap, op, pop=-2, push=-2):
    def_op(opname, opmap, op, pop, push)
    hasname.append(op)


# PyPy only
# ----------
opcode_27.def_op(opname, opmap, 'CALL_METHOD',         202)
name_op(opname, opmap, 'LOOKUP_METHOD', 201)
opcode_27.def_op(opname, opmap, 'CALL_METHOD', 202)
hasnargs.append(202)

# Used only in single-mode compilation list-comprehension generators
def_op(opname, opmap, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
jrel_op('JUMP_IF_NOT_DEBUG', 204)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

updateGlobal(2.7)

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.7 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# Remove methods so importers aren't tempted to use it.
del name_op, jrel_op, jabs_op
