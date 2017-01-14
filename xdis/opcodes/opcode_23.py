"""
CPython 2.3 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's dis.py library.

"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

from xdis.opcodes.base import (
    init_opdata)

import xdis.opcodes.opcode_2x as opcode_2x

l = locals()

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_2x.opmap)
opname = deepcopy(opcode_2x.opname)
init_opdata(l, opcode_2x)

EXTENDED_ARG = opcode_2x.EXTENDED_ARG

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def updateGlobal():
    globals().update({'python_version': 2.3})
    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opcode_2x.opname[op],
                                          opcode_2x.hasjrel + opcode_2x.hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opcode_2x.opmap.items()]))
    return

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.3:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
