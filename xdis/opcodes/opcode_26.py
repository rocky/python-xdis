"""
CPython 2.6 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's opcode.py library.
"""

from copy import deepcopy

import xdis.opcodes.opcode_25 as opcode_25
from xdis.opcodes.base import (
    def_op, init_opdata
    )

# Make a *copy* of opcode_2x values so we don't pollute 2x

l = locals()

opmap = deepcopy(opcode_25.opmap)
opname = deepcopy(opcode_25.opname)
oppush = list(opcode_25.oppush)
init_opdata(l, opcode_25)
oppop  = list(opcode_25.oppop)

EXTENDED_ARG = opcode_25.EXTENDED_ARG

def updateGlobal():
    globals().update({'python_version': 2.6})
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

# 2.6
def_op(l, 'STORE_MAP', 54, 3, 2)

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.6:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
