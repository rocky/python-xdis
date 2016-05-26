"""
CPython PYPY 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent of to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x

hasconst = list(opcode_2x.hasconst)
hascompare = list(opcode_2x.hascompare)
hasfree = list(opcode_2x.hasfree)
hasjabs = list(opcode_2x.hasjabs)
hasjrel = list(opcode_2x.hasjrel)
haslocal = list(opcode_2x.haslocal)
hasname = list(opcode_2x.hasname)
hasnargs = list(opcode_2x.hasnargs)
opmap = list(opcode_2x.opmap)
opname = list(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

def name_op(name, op):
    def_op(name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    def_op(name, op)
    hasjabs.append(op)

def updateGlobal():
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

# Bytecodes added since 2.3.
# 2.4
def_op('NOP', 9)
def_op('LIST_APPEND', 18)
def_op('YIELD_VALUE', 86)

# 2.5
def_op('WITH_CLEANUP', 81)

# 2.6
def_op('STORE_MAP', 54)

def_op('LOOKUP_METHOD', 201)
def_op('CALL_METHOD', 202)
def_op('BUILD_LIST_FROM_ARG', 203)
def_op('JUMP_IF_NOT_DEBUG', 204)

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.6 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# Remove methods so importers aren't tempted to use it.
del def_op, name_op, jrel_op, jabs_op

