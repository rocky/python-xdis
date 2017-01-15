# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is used in disassembly

This is a superset of Python 3.3's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy
from xdis.opcodes.base import (
    def_op, init_opdata, rm_op)

import xdis.opcodes.opcode_3x as opcode_3x

# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# Below are opcodes since Python 3.2

rm_op(l,  'STOP_CODE',   0)
def_op(l, 'YIELD_FROM', 72)

def updateGlobal():
    globals().update({'python_version': 3.3})

    # FIXME remove (fix uncompyle6)
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

# FIXME: turn into pytest test
from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.3:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode33.dump_opcodes(opmap)
