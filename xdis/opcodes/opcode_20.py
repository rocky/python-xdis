# (C) Copyright 2017 by Rocky Bernstein
"""
CPython 2.0 bytecode opcodes

This is similar to the opcode portion in Python 2.0's dis.py library.
"""

import xdis.opcodes.opcode_21 as opcode_21
from xdis.opcodes.base import (
    init_opdata, finalize_opcodes, format_extended_arg, rm_op, update_pj2)

version = 2.0

l = locals()
init_opdata(l, opcode_21, version)

# 2.1 Bytecodes not in 2.0
rm_op(l, 'CONTINUE_LOOP', 119)
rm_op(l, 'MAKE_CLOSURE',  134)
rm_op(l, 'LOAD_CLOSURE',  135)
rm_op(l, 'LOAD_DEREF',    136)
rm_op(l, 'STORE_DEREF',   137)

update_pj2(globals(), l)

opcode_arg_fmt = {
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
