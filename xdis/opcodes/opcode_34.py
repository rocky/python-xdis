# (C) Copyright 2017, 2020-2021, 2023 by Rocky Bernstein
"""
CPython 3.4 bytecode opcodes

This is a like Python 3.4's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_33 as opcode_33
from xdis.opcodes.base import (
    finalize_opcodes,
    format_RAISE_VARARGS_older,
    free_op,
    init_opdata,
    opcode_arg_fmt_base,
    opcode_extended_fmt_base,
    rm_op,
    update_pj3,
)
from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_30_35

version_tuple = (3, 4)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_33, version_tuple)

# fmt: off
# These are removed since Python 3.3
rm_op(loc, "STORE_LOCALS",       69)

# These are new since Python 3.3
free_op(loc, "LOAD_CLASSDEREF", 148)
# fmt: on

opcode_arg_fmt = opcode_arg_fmt34 = {
    **opcode_arg_fmt_base,
    **{
        "MAKE_CLOSURE": format_MAKE_FUNCTION_30_35,
        "MAKE_FUNCTION": format_MAKE_FUNCTION_30_35,
        "RAISE_VARARGS": format_RAISE_VARARGS_older,
    },
}

opcode_extended_fmt = opcode_extended_fmt34 = opcode_extended_fmt_base

update_pj3(globals(), loc)
finalize_opcodes(loc)
