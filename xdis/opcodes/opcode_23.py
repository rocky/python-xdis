"""
CPython 2.3 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's dis.py library.

"""

from copy import deepcopy

import xdis.opcodes.opcode_2x as opcode_2x

# FIXME: can we DRY this even more?

hasArgumentExtended = []

# Make a *copy* of opcode_2x values so we don't pollute 2x
HAVE_ARGUMENT = opcode_2x.HAVE_ARGUMENT
cmp_op = list(opcode_2x.cmp_op)
hasconst = list(opcode_2x.hasconst)
hascompare = list(opcode_2x.hascompare)
hasfree = list(opcode_2x.hasfree)
hasjabs = list(opcode_2x.hasjabs)
hasjrel = list(opcode_2x.hasjrel)
haslocal = list(opcode_2x.haslocal)
hasname = list(opcode_2x.hasname)
hasnargs = list(opcode_2x.hasnargs)
opmap = deepcopy(opcode_2x.opmap)
opname = deepcopy(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def updateGlobal():
    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opcode_2x.opname[op],
                                          opcode_2x.hasjrel + opcode_2x.hasjabs)})
    globals().update({'JA': opmap['JUMP_ABSOLUTE']})
    globals().update({'JF': opmap['JUMP_FORWARD']})
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
