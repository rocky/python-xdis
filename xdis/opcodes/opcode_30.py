"""
CPython 3.0 bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.0's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x

from xdis.opcodes.opcode_3x import fields2copy, rm_op

# FIXME: can we DRY this even more?

opmap = {}
opname = [''] * 256

cmp_op     = list(opcode_3x.cmp_op)
hasconst   = list(opcode_3x.hasconst)
hascompare = list(opcode_3x.hascompare)
hasfree    = list(opcode_3x.hasfree)
hasjabs    = list(opcode_3x.hasjabs)
hasjrel    = list(opcode_3x.hasjrel)
haslocal   = list(opcode_3x.haslocal)
hasname    = list(opcode_3x.hasname)
hasnargs   = list(opcode_3x.hasnargs)
hasvargs   = list(opcode_3x.hasvargs)
opmap = deepcopy(opcode_3x.opmap)

oppush = list(opcode_3x.oppush)
oppop  = list(opcode_3x.oppop)

for object in fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_3x, object))

# These are in Python 3.x but not in Python 3.0

rm_op('DUP_TOP_TWO',            5, locals())
rm_op('JUMP_IF_FALSE_OR_POP', 111, locals())
rm_op('JUMP_IF_TRUE_OR_POP',  112, locals())
rm_op('POP_JUMP_IF_FALSE',    114, locals())
rm_op('POP_JUMP_IF_TRUE',     115, locals())
rm_op('DELETE_DEREF',         138, locals())
rm_op('SETUP_WITH',           143, locals())
rm_op('LIST_APPEND',          145, locals())
rm_op('MAP_ADD',              147, locals())

def def_op(name, op, pop=-2, push=-2):
    opname[op] = name
    opmap[name] = op
    oppush[op] = push
    oppop[op] = pop

def jrel_op(name, op, pop=0, push=0):
    def_op(name, op, pop, push)
    hasjrel.append(op)

    # These are are in 3.0 but are not in 3.x or in 3.x they have
# different opcode numbers. Note: As a result of opcode value
# changes, these have to be applied *after* removing ops (with
# the same name).

def_op('ROT_FOUR',        5,  4, 4)
def_op('SET_ADD',        17,  1, 0)
def_op('LIST_APPEND',    18,  2, 1)
def_op('DUP_TOPX',       99)

jrel_op('JUMP_IF_FALSE', 111, 1, 1)
jrel_op('JUMP_IF_TRUE',  112, 1, 1)

# This op is in 3.x but its opcode is a 144 instead
def_op('EXTENDED_ARG',  143)

def updateGlobal():
    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'python_version': 3.0})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.0:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    for item in dis.opmap.items():
        assert item in opmap.items()
    for item in opmap.items():
        assert item in opmap.items()

# opcode_30.dump_opcodes(opmap)
