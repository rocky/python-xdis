"""
CPython 2.1 bytecode opcodes

This is used in bytecode disassembly. This is equivalent to the
opcodes in Python's dis.py library.

"""

from copy import deepcopy

import sys

if sys.version_info[0:2] > (2,1):
    import xdis.opcodes.opcode_2x as opcode_2x
    from xdis.opcodes.opcode_2x import findlabels, findlinestarts
    from xdis.opcodes.opcode_2x import def_op
else:
    import opcode_2x
    from opcode_2x import def_op

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
hasvargs = list(opcode_2x.hasvargs)
opmap = deepcopy(opcode_2x.opmap)
opname = deepcopy(opcode_2x.opname)
EXTENDED_ARG = opcode_2x.EXTENDED_ARG

def rm_op(name, op):
    # opname is an array, so we need to keep the position in there.
    opname[op] = '<%s>' % op

# 2.3 Bytecodes not in 2.1
rm_op('BINARY_FLOOR_DIVIDE', 26)
rm_op('BINARY_TRUE_DIVIDE', 27)
rm_op('BINARY_INPLACE_DIVIDE', 28)
rm_op('INPLACE_TURE_DIVIDE', 29)
rm_op('GET_ITER', 68)
rm_op('YIELD_VALUE', 86)
rm_op('FOR_ITER', 93)

# 2.1 Bytecodes not in 2.3
def_op(opname, opmap, 'FOR_LOOP', 114)
def_op(opname, opmap, 'SET_LINENO', 127)

for object in opcode_2x.fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_2x, object))

def updateGlobal():
    globals().update({'python_version': 2.1})
    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opcode_2x.opname[op],
                                          opcode_2x.hasjrel + opcode_2x.hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opcode_2x.opmap.items()]))
    return

updateGlobal()

if sys.version_info[0:2] == (2,1):
    import dis
    assert len(opname) == len(dis.opname)
    for i in range(len(dis.opname)):
        assert dis.opname[i] == opname[i], [i, dis.opname[i], opname[i]]
