"""
CPython 3.4 bytecode opcodes

used in scanner (bytecode disassembly) and parser (Python grammar)

This is a superset of Python 3.4's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

import xdis.opcodes.opcode_3x as opcode_3x

# These are used from outside this module
from xdis.opcodes.opcode_3x import findlabels, findlinestarts

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

def free_op(name, op):
    def_op(name, op)
    hasfree.append(op)

for object in fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_3x, object))

# Below are opcodes changes since Python 3.2

rm_op('STOP_CODE', 0, locals())
rm_op('STORE_LOCALS', 69, locals())

# These are new since Python 3.3
def_op('YIELD_FROM', 72)
free_op('LOAD_CLASSDEREF', 148)

def updateGlobal():
    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'python_version': 3.4})
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.4:
    import dis
    # for item in dis.opmap.items():
    #     if item not in opmap.items():
    #         print(item)
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# opcode_34.dump_opcodes(opmap)
