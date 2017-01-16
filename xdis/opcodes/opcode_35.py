# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.5 bytecode opcodes

This is a like Python 3.5's opcode.py with some classification
of stack usage.
"""

from copy import deepcopy
from xdis.opcodes.base import (
    def_op, init_opdata, rm_op)

import xdis.opcodes.opcode_34 as opcode_34

# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_34 values so we don't pollute 34
opmap = deepcopy(opcode_34.opmap)
opname = deepcopy(opcode_34.opname)
init_opdata(l, opcode_34)

# These are removed since Python 3.5.
# Removals happen before adds since
# some opcodes are reused
rm_op(l, 'STORE_MAP',                    54)
rm_op(l, 'WITH_CLEANUP',                 81)

# These are new since Python 3.5
def_op(l, 'BINARY_MATRIX_MULTIPLY',      16,  2, 1)
def_op(l, 'INPLACE_MATRIX_MULTIPLY',     17,  2, 1)
def_op(l, 'GET_AITER',                   50,  1, 1)
def_op(l, 'GET_ANEXT',                   51,  0, 1)
def_op(l, 'BEFORE_ASYNC_WITH',           52)
def_op(l, 'GET_YIELD_FROM_ITER',         69)
def_op(l, 'GET_AWAITABLE',               73,  0, 0)
def_op(l, 'WITH_CLEANUP_START',          81,  0, 1)
def_op(l, 'WITH_CLEANUP_FINISH',         82, -1, 1)
def_op(l, 'BUILD_LIST_UNPACK',          149, -1, 1)
def_op(l, 'BUILD_MAP_UNPACK',           150, -1, 1)
def_op(l, 'BUILD_MAP_UNPACK_WITH_CALL', 151, -1, 1)
def_op(l, 'BUILD_TUPLE_UNPACK',         152, -1, 1)
def_op(l, 'BUILD_SET_UNPACK',           153, -1, 1)
def_op(l, 'SETUP_ASYNC_WITH',           154,  0, 6)

def updateGlobal():
    globals().update({'python_version': 3.5})

    # FIXME: Get rid of these (change uncompyle)
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update({'JF': opmap['JUMP_FORWARD']})

    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

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
