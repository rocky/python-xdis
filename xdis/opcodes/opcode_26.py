"""
CPython 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

from xdis.opcodes.opcode_2x import def_op
import xdis.opcodes.opcode_25 as opcode_25

# FIXME: can we DRY this even more?

hasArgumentExtended = []

# Make a *copy* of opcode_2x values so we don't pollute 2x

HAVE_ARGUMENT = opcode_25.HAVE_ARGUMENT
cmp_op = list(opcode_25.cmp_op)
hasconst = list(opcode_25.hasconst)
hascompare = list(opcode_25.hascompare)
hasfree = list(opcode_25.hasfree)
hasjabs = list(opcode_25.hasjabs)
hasjrel = list(opcode_25.hasjrel)
haslocal = list(opcode_25.haslocal)
hasname = list(opcode_25.hasname)
hasnargs = list(opcode_25.hasnargs)
hasvargs = list(opcode_25.hasvargs)
opmap = deepcopy(opcode_25.opmap)
opname = deepcopy(opcode_25.opname)
EXTENDED_ARG = opcode_25.EXTENDED_ARG

def updateGlobal():
    globals().update({'python_version': 2.6})
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

# 2.6
def_op(opname, opmap, 'STORE_MAP', 54)

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.6:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
