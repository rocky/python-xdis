# (C) Copyright 2016-2017 by Rocky Bernstein
"""
CPython 3.2 bytecode opcodes

This is a like Python 3.2's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_3x as opcode_3x
from xdis.opcodes.base import (
    finalize_opcodes, format_extended_arg, init_opdata,
    update_pj3)

from xdis.opcodes.opcode_3x import format_MAKE_FUNCTION_arg

# FIXME: can we DRY this even more?

version = 3.2

l = locals()

init_opdata(l, opcode_3x, version)

# There are no opcodes to add or change.
# If there were, they'd be listed below.

update_pj3(globals(), l)

opcode_arg_fmt = {
    'MAKE_FUNCTION': format_MAKE_FUNCTION_arg,
    'EXTENDED_ARG': format_extended_arg,
}

finalize_opcodes(l)
