"""
CPython 3.2 PYPY bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.2's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy

from xdis.opcodes.base import (
    def_op, init_opdata, jrel_op, name_op,
    varargs_op)

l = locals()

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x

# FIXME: can we DRY this even more?

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# PyPy only
# ----------
name_op(l, 'LOOKUP_METHOD',  201,  1, 2)

varargs_op(l, 'CALL_METHOD', 202, -1, 1)
l['hasnargs'].append(202)
hasvargs = list(opcode_3x.hasvargs)

# Used only in single-mode compilation list-comprehension generators
def_op(l, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
jrel_op(l, 'JUMP_IF_NOT_DEBUG', 204)

# There are no opcodes to remove or change.
# If there were, they'd be listed below.

def updateGlobal():
    globals().update({'python_version': 3.2})

    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

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
