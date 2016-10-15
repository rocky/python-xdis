"""
CPython 2.4 bytecode opcodes

This is used in bytecode disassembly.

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.opcode_2x import def_op

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
    globals().update({'python_version': 2.4})
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

# Bytecodes added since 2.3
def_op(opname, opmap, 'NOP', 9)
def_op(opname, opmap, 'LIST_APPEND', 18)
def_op(opname, opmap, 'YIELD_VALUE', 86)

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.4:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
