# (C) Copyright 2017, 2020 by Rocky Bernstein
"""
CPython 2.5 bytecode opcodes

This is a like Python 2.5's opcode.py with some additional classification
of stack usage, and opererand formatting functions.
"""

import xdis.opcodes.opcode_24 as opcode_24
from xdis.opcodes.base import (
    def_op,
    extended_format_CALL_FUNCTION,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RETURN_VALUE,
    init_opdata,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_MAKE_FUNCTION_default_argc,
    format_extended_arg,
    update_pj2,
    )

version = 2.5
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_24, version)

# Bytecodes added in 2.5 from 2.4
#          OP NAME            OPCODE POP PUSH
#--------------------------------------------
def_op(l, 'WITH_CLEANUP',      81,   4,  3)

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_KW": format_CALL_FUNCTION_pos_name_encoded,
    "CALL_FUNCTION_VAR_KW": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_FUNCTION": format_MAKE_FUNCTION_default_argc,

}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
}
finalize_opcodes(l)
