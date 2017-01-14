# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 3.1 bytecode opcodes

This is used in scanner (bytecode disassembly) and parser (Python grammar).

This is a superset of Python 3.1's opcode.py with some opcodes that simplify
parsing and semantic interpretation.
"""

from copy import deepcopy
from xdis.opcodes.base import (
    def_op, init_opdata,
    rm_op)

l = locals()

# These are used from outside this module
from xdis.bytecode import findlinestarts, findlabels

import xdis.opcodes.opcode_3x as opcode_3x

# FIXME: can we DRY this even more?

l = locals()

# Make a *copy* of opcode_2x values so we don't pollute 2x
opmap = deepcopy(opcode_3x.opmap)
opname = deepcopy(opcode_3x.opname)
init_opdata(l, opcode_3x)

# These are in Python 3.x but not in Python 3.1
rm_op(l, 'DUP_TOP_TWO',    5)
rm_op(l, 'DELETE_DEREF', 138)
rm_op(l, 'SETUP_WITH',   143)

# These are in Python 3.1 but not Python 3.x
def_op(l, 'ROT_FOUR', 5)
def_op(l, 'DUP_TOPX', 99)

# This op is in 3.x but its opcode is a 144 instead
def_op(l, 'EXTENDED_ARG', 143)

def updateGlobal():
    globals().update({'python_version': 3.1})

    # FIXME remove (fix uncompyle6)
    globals().update({'PJIF': opmap['POP_JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['POP_JUMP_IF_TRUE']})

    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))

    # JUMP_OPs are used in verification are set in the scanner
    # and used in the parser grammar
    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      l['hasjrel'] + l['hasjabs'])})

updateGlobal()

from xdis import PYTHON_VERSION
if PYTHON_VERSION == 3.1:
    import dis
    # print(set(dis.opmap.items()) - set(opmap.items()))
    # print(set(opmap.items()) - set(dis.opmap.items()))

    assert all(item in dis.opmap.items() for item in opmap.items())
    assert all(item in opmap.items() for item in dis.opmap.items())

# opcode_31.dump_opcodes(opmap)
