"""
CPython 2.7 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.opcode_2x import def_op, rm_op

# FIXME: can we DRY this even more?

hasArgumentExtended = []  # for compatibility with 2.5-2.6

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
    globals().update({'python_version': 2.7})

    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

def name_op(name, op):
    def_op(opname, opmap, name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(opname, opmap, name, op)
    hasjrel.append(op)

def jabs_op(name, op):
    def_op(opname, opmap, name, op)
    hasjabs.append(op)

def compare_op(name, op):
    def_op(opname, opmap, name, op)
    hascompare.append(op)

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
name_op('LOAD_ATTR', 106)
compare_op('COMPARE_OP', 107)

name_op('IMPORT_NAME', 108)
name_op('IMPORT_FROM', 109)

jabs_op('JUMP_IF_FALSE_OR_POP', 111) # Target byte offset from beginning of code
jabs_op('JUMP_IF_TRUE_OR_POP', 112)  # ""
jabs_op('POP_JUMP_IF_FALSE', 114)    # ""
jabs_op('POP_JUMP_IF_TRUE', 115)     # ""
jrel_op('SETUP_WITH', 143)

def_op(opname, opmap, 'EXTENDED_ARG', 145)
def_op(opname, opmap, 'SET_ADD', 146)
def_op(opname, opmap, 'MAP_ADD', 147)

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 2.7 and not IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# Remove methods so importers aren't tempted to use it.
del name_op, jrel_op, jabs_op
