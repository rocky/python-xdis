"""
CPython 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent of to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.opcode_2x import def_op

hasArgumentExtended = []

hasconst = list(opcode_2x.hasconst)
hascompare = list(opcode_2x.hascompare)
hasfree = list(opcode_2x.hasfree)
hasjabs = list(opcode_2x.hasjabs)
hasjrel = list(opcode_2x.hasjrel)
haslocal = list(opcode_2x.haslocal)
hasnargs = list(opcode_2x.hasnargs)
opmap = list(opcode_2x.opmap)
opname = list(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def updateGlobal():
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update({'JA': opmap['JUMP_ABSOLUTE']})
    globals().update({'JF': opmap['JUMP_FORWARD']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return


# Bytecodes added since 2.3.
# 2.4
def_op(opname, opmap, 'NOP', 9)
def_op(opname, opmap, 'LIST_APPEND', 18)
hasArgumentExtended.append(18)

def_op(opname, opmap, 'YIELD_VALUE', 86)

# 2.5
def_op(opname, opmap, 'WITH_CLEANUP', 81)

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
