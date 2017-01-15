# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

from copy import deepcopy
from xdis.opcodes.base import (
    def_op, free_op, init_opdata, rm_op
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

def updateGlobal():
    globals().update({'python_version': 3.4})
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.4:
    import dis
    # for item in dis.opmap.items():
    #     if item not in opmap.items():
    #         print(item)
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())

# opcode_34.dump_opcodes(opmap)
