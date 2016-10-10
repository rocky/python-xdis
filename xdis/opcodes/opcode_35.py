# (C) Copyright 2016 by Rocky Bernstein
"""
CPython 3.5 bytecode opcodes

used in scanner (bytecode disassembly) and parser (Python grammar)

This is a superset of Python 3.5's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.opcode_3x import fields2copy, hasfree, rm_op

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

# These are removed since Python 3.4
rm_op('WITH_CLEANUP', 81, locals())

# These are new since Python 3.5
def_op('BINARY_MATRIX_MULTIPLY', 16)
def_op('INPLACE_MATRIX_MULTIPLY', 17)
def_op('GET_AITER', 50)
def_op('GET_ANEXT', 51)
def_op('BEFORE_ASYNC_WITH', 52)
def_op('GET_YIELD_FROM_ITER', 69)
def_op('GET_AWAITABLE', 73)
def_op('WITH_CLEANUP_START', 81)
def_op('WITH_CLEANUP_FINISH', 82)
def_op('BUILD_LIST_UNPACK', 149)
def_op('BUILD_MAP_UNPACK', 150)
def_op('BUILD_MAP_UNPACK_WITH_CALL', 151)
def_op('BUILD_TUPLE_UNPACK', 152)
def_op('BUILD_SET_UNPACK', 153)
def_op('SETUP_ASYNC_WITH', 154)
rm_op('STORE_MAP', 54, locals())

def updateGlobal():
    globals().update({'python_version': 3.5})
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update({'JF': opmap['JUMP_FORWARD']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.5:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode_35.dump_opcodes(opmap)
