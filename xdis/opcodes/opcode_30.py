# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.0 bytecode opcodes

This is a like Python 3.0's opcode.py with some classification
of stack usage.
"""

from copy import deepcopy

from xdis.opcodes.base import (
    def_op, init_opdata,
    jrel_op, rm_op)

import xdis.opcodes.opcode_3x as opcode_3x

# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_3x values so we don't pollute 3x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# These are in Python 3.x but not in Python 3.0

rm_op(l, 'DUP_TOP_TWO',            5)
rm_op(l, 'JUMP_IF_FALSE_OR_POP', 111)
rm_op(l, 'JUMP_IF_TRUE_OR_POP',  112)
rm_op(l, 'POP_JUMP_IF_FALSE',    114)
rm_op(l, 'POP_JUMP_IF_TRUE',     115)
rm_op(l, 'DELETE_DEREF',         138)
rm_op(l, 'SETUP_WITH',           143)
rm_op(l, 'LIST_APPEND',          145)
rm_op(l, 'MAP_ADD',              147)

# These are are in 3.0 but are not in 3.x or in 3.x they have
# different opcode numbers. Note: As a result of opcode value
# changes, these have to be applied *after* removing ops (with
# the same name).

def_op(l, 'ROT_FOUR',        5,  4, 4)
def_op(l, 'SET_ADD',        17,  1, 0)
def_op(l, 'LIST_APPEND',    18,  2, 1)
def_op(l, 'DUP_TOPX',       99)

jrel_op(l, 'JUMP_IF_FALSE', 111, 1, 1)
jrel_op(l, 'JUMP_IF_TRUE',  112, 1, 1)

# This op is in 3.x but its opcode is a 144 instead
def_op(l, 'EXTENDED_ARG',  143)

def updateGlobal():
    globals().update({'python_version': 3.0})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.0:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode_30.dump_opcodes(opmap)
