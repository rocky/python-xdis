"""
CPython PYPY 2.7 bytecode opcodes

This is used in bytecode disassembly. This is equivalent of to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.opcode_2x import def_op, rm_op

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

def name_op(name, op):
    def_op(opname, opmap, name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(opname, opmap, name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    def_op(opname, opmap, name, op)
    hasjabs.append(op)

def updateGlobal():
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

# Bytecodes added since 2.3.
# 2.4
def_op(opname, opmap, 'NOP', 9)
def_op(opname, opmap, 'YIELD_VALUE', 86)

# 2.5
def_op(opname, opmap, 'WITH_CLEANUP', 81)

# 2.6
def_op(opname, opmap, 'STORE_MAP', 54)

# 2.7
rm_op('BUILD_MAP', 104, locals())
rm_op('LOAD_ATTR', 105, locals())
rm_op('COMPARE_OP', 106, locals())
rm_op('IMPORT_NAME', 107, locals())
rm_op('IMPORT_FROM', 108, locals())
rm_op('JUMP_IF_FALSE', 111, locals())
rm_op('EXTENDED_ARG', 143, locals())
rm_op('JUMP_IF_TRUE', 112, locals())

def_op(opname, opmap, 'LIST_APPEND', 94)
def_op(opname, opmap, 'BUILD_SET', 104)        # Number of set items
def_op(opname, opmap, 'BUILD_MAP', 105)
def_op(opname, opmap, 'LOAD_ATTR', 106)
def_op(opname, opmap, 'COMPARE_OP', 107)
def_op(opname, opmap, 'IMPORT_NAME', 108)
def_op(opname, opmap, 'IMPORT_FROM', 109)

jabs_op('JUMP_IF_FALSE_OR_POP', 111) # Target byte offset from beginning of code
jabs_op('JUMP_IF_TRUE_OR_POP', 112)  # ""
jabs_op('POP_JUMP_IF_FALSE', 114)    # ""
jabs_op('POP_JUMP_IF_TRUE', 115)     # ""
jrel_op('SETUP_WITH', 143)

def_op(opname, opmap, 'EXTENDED_ARG', 145)
def_op(opname, opmap, 'SET_ADD', 146)
def_op(opname, opmap, 'MAP_ADD', 147)

def_op(opname, opmap, 'LOOKUP_METHOD', 201)
def_op(opname, opmap, 'CALL_METHOD', 202)
def_op(opname, opmap, 'BUILD_LIST_FROM_ARG', 203)
def_op(opname, opmap, 'JUMP_IF_NOT_DEBUG', 204)

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.7 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# Remove methods so importers aren't tempted to use it.
del name_op, jrel_op, jabs_op
