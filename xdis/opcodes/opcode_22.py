# (C) Copyright 2017, 2019, 2021 by Rocky Bernstein
"""
CPython 2.2 bytecode opcodes

This is similar to the opcode portion in Python 2.2's dis.py library.
"""

import xdis.opcodes.opcode_2x as opcode_2x
from xdis.opcodes.base import (
    def_op,
    extended_format_ATTR,
    extended_format_MAKE_FUNCTION_older,
    extended_format_RETURN_VALUE,
    init_opdata,
    finalize_opcodes,
    format_extended_arg,
    update_pj2,
)

version = 2.2
version_tuple = (2, 2)
python_implementation = "CPython"

l = locals()
init_opdata(l, opcode_2x, version_tuple)

# 2.2 Bytecodes not in 2.3
def_op(l, "FOR_LOOP", 114)
def_op(l, "SET_LINENO", 127, 0, 0)

update_pj2(globals(), l)


finalize_opcodes(l)

opcode_arg_fmt = {"EXTENDED_ARG": format_extended_arg}

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_FUNCTION": extended_format_MAKE_FUNCTION_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
