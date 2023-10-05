# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 3.3 bytecode opcodes

This is a like Python 3.3's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import def_op, finalize_opcodes, init_opdata, rm_op, update_pj3
from xdis.opcodes.format.basic import format_RAISE_VARARGS_older, opcode_arg_fmt_base
from xdis.opcodes.format.extended import opcode_extended_fmt_base
from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_30_35

version_tuple = (3, 3)
python_implementation = "CPython"

loc = locals()
init_opdata(loc, opcode_3x, version_tuple)

# Below are opcode changes since Python 3.2

# fmt: off
rm_op(loc,  "STOP_CODE",   0)
def_op(loc, "YIELD_FROM", 72, 1, 0)
# fmt: on


opcode_extended_fmt = opcode_extended_fmt33 = opcode_extended_fmt_base.copy()
opcode_arg_fmt = opcode_arg_fmt33 = {
    **opcode_arg_fmt_base,
    **{
        "MAKE_CLOSURE": format_MAKE_FUNCTION_30_35,
        "MAKE_FUNCTION": format_MAKE_FUNCTION_30_35,
        "RAISE_VARARGS": format_RAISE_VARARGS_older,
    },
}

update_pj3(globals(), loc)
finalize_opcodes(loc)
