# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.2 bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.2's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import (
    init_opdata)

# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# There are no opcodes to add or change.
# If there were, they'd be listed below.

def updateGlobal():
    globals().update({'python_version': 3.2})

    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 3.2:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    if not IS_PYPY:
        assert all(item in opmap.items() for item in dis.opmap.items())
        assert all(item in dis.opmap.items() for item in opmap.items())

# opcode_3x.dump_opcodes(opmap)
