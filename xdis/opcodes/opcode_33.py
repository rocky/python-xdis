"""
CPython 3.3 bytecode opcodes

This is used in disassembly

This is a superset of Python 3.3's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.opcodes.opcode_3x import findlabels, findlinestarts

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.opcode_3x import fields2copy, rm_op

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

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

for object in fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_3x, object))

# Below are opcodes since Python 3.2

rm_op('STOP_CODE', 0, locals())

def_op('YIELD_FROM', 72)

def updateGlobal():
    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'python_version': 3.3})
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.3:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode33.dump_opcodes(opmap)
