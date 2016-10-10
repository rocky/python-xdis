"""
CPython 3.2 bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.2's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.opcode_3x import def_op, fields2copy

# FIXME: can we DRY this even more?

opmap = {}
opname = [''] * 256
hasjrel = list(opcode_3x.hasjrel)
hasjabs = []
hasname = list(opcode_3x.hasname)
hasnargs = list(opcode_3x.hasnargs)

for object in fields2copy:
    globals()[object] =  deepcopy(getattr(opcode_3x, object))

def name_op(name, op):
    def_op(opname, opmap, name, op)
    hasname.append(op)

def jrel_op(name, op):
    def_op(opname, opmap, name, op)
    hasjrel.append(op)

# PyPy only
# ----------
name_op('LOOKUP_METHOD', 201)
def_op(opname, opmap, 'CALL_METHOD', 202)
hasnargs.append(202)

# Used only in single-mode compilation list-comprehension generators
def_op(opname, opmap, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
jrel_op('JUMP_IF_NOT_DEBUG', 204)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

def updateGlobal():
    globals().update({'python_version': 3.2})

    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op], hasjrel + hasjabs)})

updateGlobal()

from xdis import PYTHON_VERSION, IS_PYPY
if PYTHON_VERSION == 3.2 and IS_PYPY:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))
    # for item in dis.opmap.items():
    if IS_PYPY:
        assert all(item in opmap.items() for item in dis.opmap.items())
        assert all(item in dis.opmap.items() for item in opmap.items())

# opcode_3x.dump_opcodes(opmap)
