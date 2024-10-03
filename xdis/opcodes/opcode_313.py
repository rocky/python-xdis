"""
CPython 3.13 bytecode opcodes
"""

import xdis.opcodes.opcode_312 as opcode_312
from xdis.opcodes.base import (
    binary_op,
    def_op,
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    rm_op,
    update_pj3,
)

version_tuple = (3, 13)
python_implementation = "CPython"

loc = locals()

init_opdata(loc, opcode_312, version_tuple)

# fmt: off
## These are removed / replaced since 3.12...
#           OP NAME                      OPCODE
#----------------------------------------------

## These are new since 3.12...
#            OP NAME                              OPCODE POP PUSH
# ---------------------------------------------------------------

### update formatting
opcode_arg_fmt313 = opcode_312.opcode_arg_fmt12
opcode_extended_fmt = opcode_extended_fmt313 = opcode_312.opcode_extended_fmt312.copy()
from xdis.opcodes.opcode_312 import findlinestarts, parse_location_entries, format_CALL_INTRINSIC_1, format_CALL_INTRINSIC_2
opcode_arg_fmt = opcode_arg_fmt13 = opcode_312.opcode_arg_fmt312.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
