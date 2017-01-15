# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.6 bytecode opcodes

This is a like Python 3.6's opcode.py with some classification
of stack usage.
"""

from copy import deepcopy
from xdis.opcodes.base import(
    def_op, init_opdata, nargs_op, rm_op, varargs_op
    )

import xdis.opcodes.opcode_35 as opcode_35

l = locals()

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_35 values so we don't pollute 3.5
opmap = deepcopy(opcode_35.opmap)
opname = deepcopy(opcode_35.opname)
init_opdata(l, opcode_35)

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
