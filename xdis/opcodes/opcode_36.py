# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.6 bytecode opcodes

used in scanner (bytecode disassembly) and parser (Python grammar)

This is a superset of Python 3.6's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy
from xdis.opcodes.base import(
    def_op, free_op, init_opdata, nargs_op, rm_op, varargs_op
    )

import xdis.opcodes.opcode_3x as opcode_3x

l = locals()

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# Below are opcodes changes since Python 3.2

rm_op(l, 'STOP_CODE',     0)
rm_op(l, 'STORE_LOCALS', 69)

# These are new since Python 3.3
def_op(l,  'YIELD_FROM',       72)
free_op(l, 'LOAD_CLASSDEREF', 148)

# These are removed since Python 3.4
rm_op(l, 'WITH_CLEANUP', 81)

# These are new since Python 3.5
def_op(l, 'BINARY_MATRIX_MULTIPLY',      16)
def_op(l, 'INPLACE_MATRIX_MULTIPLY',     17)
def_op(l, 'GET_AITER',                   50)
def_op(l, 'GET_ANEXT',                   51)
def_op(l, 'BEFORE_ASYNC_WITH',           52)
def_op(l, 'GET_YIELD_FROM_ITER',         69)
def_op(l, 'GET_AWAITABLE',               73)
def_op(l, 'WITH_CLEANUP_START',          81)
def_op(l, 'WITH_CLEANUP_FINISH',         82)
def_op(l, 'BUILD_LIST_UNPACK',          149)
def_op(l, 'BUILD_MAP_UNPACK',           150)
def_op(l, 'BUILD_MAP_UNPACK_WITH_CALL', 151)
def_op(l, 'BUILD_TUPLE_UNPACK',         152)
def_op(l, 'BUILD_SET_UNPACK',           153)
def_op(l, 'SETUP_ASYNC_WITH',           154)

rm_op(l, 'STORE_MAP', 54)

# These are removed since Python 3.6
rm_op(l, 'MAKE_CLOSURE',         134)
rm_op(l, 'CALL_FUNCTION_VAR',    140)
rm_op(l, 'CALL_FUNCTION_VAR_KW', 142)


# These are new since Python 3.6
def_op(l, 'FORMAT_VALUE', 155)
varargs_op(l, 'BUILD_CONST_KEY_MAP', 156, -1, 1) # TOS is count of kwargs
def_op(l, 'STORE_ANNOTATION', 127)
nargs_op(l, 'CALL_FUNCTION_EX', 142, -1, 1)
def_op(l, 'SETUP_ANNOTATIONS', 85)
def_op(l, 'BUILD_STRING', 157)
def_op(l, 'BUILD_TUPLE_UNPACK_WITH_CALL', 158)

def updateGlobal():
    globals().update({'python_version': 3.6})

    # FIXME remove (fix uncompyle6)
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.6:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# opcode_36x.dump_opcodes(opmap)
