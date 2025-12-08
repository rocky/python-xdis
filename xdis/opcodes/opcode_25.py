# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 2.5 bytecode opcodes

This is a like Python 2.5's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
"""

import xdis.opcodes.opcode_24 as opcode_24
from xdis.opcodes.base import (  # noqa
    cpython_implementation as python_implementation,
    def_op,
    finalize_opcodes,
    init_opdata,
    update_pj2,
)
from xdis.opcodes.opcode_2x import opcode_extended_fmt_base2x, update_arg_fmt_base2x

version_tuple = (2, 5)

loc = locals()
init_opdata(loc, opcode_24, version_tuple)

# fmt: off
# Bytecodes added in 2.5 from 2.4
#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
def_op(loc, 'WITH_CLEANUP',      81,   4,  3)
# fmt: on

opcode_arg_fmt = update_arg_fmt_base2x.copy()
opcode_extended_fmt = opcode_extended_fmt12 = opcode_extended_fmt_base2x.copy()

# FIXME remove (fix uncompyle6)
update_pj2(globals(), loc)
finalize_opcodes(loc)
