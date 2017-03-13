# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.6 bytecode opcodes

This is a like Python 3.6's opcode.py with some classification
of stack usage.
"""

from xdis.opcodes.base import(
    def_op, finalize_opcodes,
    init_opdata, nargs_op, rm_op, varargs_op,
    update_pj3
    )

import xdis.opcodes.opcode_35 as opcode_35

version = 3.6

l = locals()

init_opdata(l, opcode_35, version)

# These are removed since Python 3.6
rm_op(l, 'MAKE_CLOSURE',         134)
rm_op(l, 'CALL_FUNCTION_VAR',    140)
rm_op(l, 'CALL_FUNCTION_VAR_KW', 142)


# These are new since Python 3.6
def_op(l, 'FORMAT_VALUE', 155)
varargs_op(l, 'BUILD_CONST_KEY_MAP', 156, -1, 1) # TOS is count of kwargs
def_op(l, 'STORE_ANNOTATION', 127)
nargs_op(l, 'CALL_FUNCTION_EX', 142, -1, 1)
def_op(l, 'SETUP_ANNOTATIONS', 85)
def_op(l, 'BUILD_STRING', 157)
def_op(l, 'BUILD_TUPLE_UNPACK_WITH_CALL', 158)

update_pj3(globals(), l)

finalize_opcodes(l)
