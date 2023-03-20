# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import (
    def_op,
    extended_format_CALL_FUNCTION,
    extended_format_RAISE_VARARGS_older,
    extended_format_RETURN_VALUE,
    finalize_opcodes,
    format_CALL_FUNCTION_pos_name_encoded,
    format_extended_arg,
    format_RAISE_VARARGS_older,
    init_opdata,
    rm_op,
    update_pj3,
)

version_tuple = (3, 3)
python_implementation = "CPython"

loc = l = locals()
init_opdata(l, opcode_3x, version_tuple)

# Below are opcode changes since Python 3.2

# fmt: off
rm_op(l,  "STOP_CODE",   0)
def_op(l, "YIELD_FROM", 72, 1, 0)
# fmt: on


update_pj3(globals(), l)

finalize_opcodes(l)


def extended_format_ATTR(opc, instructions):
    if instructions[1].opname in (
        "LOAD_CONST",
        "LOAD_GLOBAL",
        "LOAD_ATTR",
        "LOAD_NAME",
    ):
        return "%s.%s " % (instructions[1].argrepr, instructions[0].argrepr)


opcode_arg_fmt = {
    "CALL_FUNCTION": format_CALL_FUNCTION_pos_name_encoded,
    "EXTENDED_ARG": format_extended_arg,
    "MAKE_CLOSURE": opcode_3x.format_MAKE_FUNCTION_30_35,
    "MAKE_FUNCTION": opcode_3x.format_MAKE_FUNCTION_30_35,
    "RAISE_VARARGS": format_RAISE_VARARGS_older,
}

opcode_extended_fmt = {
    "CALL_FUNCTION": extended_format_CALL_FUNCTION,
    "LOAD_ATTR": extended_format_ATTR,
    "MAKE_CLOSURE": opcode_3x.extended_format_MAKE_FUNCTION_30_35,
    "MAKE_FUNCTION": opcode_3x.extended_format_MAKE_FUNCTION_30_35,
    "RAISE_VARARGS": extended_format_RAISE_VARARGS_older,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}
