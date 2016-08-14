"""
CPython 2.5 bytecode opcodes

This is used in bytecode disassembly.

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.opcodes.opcode_2x import findlabels, findlinestarts

from xdis.opcodes.opcode_2x import def_op
import xdis.opcodes.opcode_24 as opcode_24

hasArgumentExtended = []

# Make a *copy* of opcode_2x values so we don't pollute 2x
HAVE_ARGUMENT = opcode_24.HAVE_ARGUMENT
cmp_op = list(opcode_24.cmp_op)
hasconst = list(opcode_24.hasconst)
hascompare = list(opcode_24.hascompare)
hasfree = list(opcode_24.hasfree)
hasjabs = list(opcode_24.hasjabs)
hasjrel = list(opcode_24.hasjrel)
haslocal = list(opcode_24.haslocal)
hasname = list(opcode_24.hasname)
hasnargs = list(opcode_24.hasnargs)
hasvargs = list(opcode_24.hasvargs)
opmap = deepcopy(opcode_24.opmap)
opname = deepcopy(opcode_24.opname)
EXTENDED_ARG = opcode_24.EXTENDED_ARG

def updateGlobal():
    globals().update({'python_version': 2.5})
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

# 2.5
def_op(opname, opmap, 'WITH_CLEANUP', 81)

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.5:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
