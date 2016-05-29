"""
CPython 2.3 bytecode opcodes

This is used in bytecode disassembly. This is equivalent of to the
opcodes in Python's dis.py library.

"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_2x values so we don't pollute 2x
hasconst = list(opcode_2x.hasconst)
hascompare = list(opcode_2x.hascompare)
hasfree = list(opcode_2x.hasfree)
haslocal = list(opcode_2x.haslocal)
hasnargs = list(opcode_2x.hasnargs)
opmap = list(opcode_2x.opmap)
opname = list(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def updateGlobal():
    # This makes things look more like 2.7
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opcode_2x.opname[op],
                                          opcode_2x.hasjrel + opcode_2x.hasjabs)})
    globals().update({'JA': opmap['JUMP_ABSOLUTE']})
    globals().update({'JF': opmap['JUMP_FORWARD']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opcode_2x.opmap.items()]))
    return

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 2.3:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    assert all(item in opmap.items() for item in dis.opmap.items())
    assert all(item in dis.opmap.items() for item in opmap.items())
