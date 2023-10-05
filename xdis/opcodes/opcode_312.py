"""
CPython 3.12 bytecode opcodes

This is like Python 3.12's opcode.py  with some classification
of stack usage and information for formatting instructions.
"""

from typing import Optional

import xdis.opcodes.opcode_311 as opcode_311
from xdis.opcodes.base import (
    binary_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    rm_op,
    update_pj3,
)
from xdis.opcodes.format.extended import extended_format_binary_op

version_tuple = (3, 12)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_311, version_tuple)

# fmt: off
## These are removed / replaced since 3.11...
#         OP NAME                 OPCODE
#---------------------------------------
# Binary ops

###############
### NEW OPS ###
###############

update_pj3(globals(), loc)
finalize_opcodes(loc)
