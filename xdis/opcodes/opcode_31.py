"""
CPython 3.1 bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.1's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy
from xdis.opcodes.base import def_op, rm_op

l = locals()

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.opcode_3x import fields2copy

# FIXME: can we DRY this even more?

opmap = {}
opname = [''] * 256
hasconst = list(opcode_3x.hasconst)
hascompare = list(opcode_3x.hascompare)
hasfree = list(opcode_3x.hasfree)
hasjabs = list(opcode_3x.hasjabs)
hasjrel = list(opcode_3x.hasjrel)
haslocal = list(opcode_3x.haslocal)
hasname = list(opcode_3x.hasname)
hasnargs = list(opcode_3x.hasnargs)
hasvargs = list(opcode_3x.hasvargs)
oppush = list(opcode_3x.oppush)
oppop  = list(opcode_3x.oppop)

for object in fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_3x, object))

# These are in Python 3.x but not in Python 3.1
rm_op('DUP_TOP_TWO',    5, l)
rm_op('DELETE_DEREF', 138, l)
rm_op('SETUP_WITH',   143, l)

# These are in Python 3.1 but not Python 3.x
def_op(l, 'ROT_FOUR', 5)
def_op(l, 'DUP_TOPX', 99)

# This op is in 3.x but its opcode is a 144 instead
def_op(l, 'EXTENDED_ARG', 143)

# There are no opcodes to add or change.
# If there were, they'd be listed below.

def updateGlobal():
    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'python_version': 3.1})
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.1:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode_31.dump_opcodes(opmap)
