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
rm_op(loc, "LOAD_CLOSURE", 136)  # now a psuedo-instruction, replaced with LOAD_FAST

## These are new since 3.12...
#            OP NAME                              OPCODE POP PUSH
# ---------------------------------------------------------------
def_op(loc, "TO_BOOL", 40, 0, 0)
def_op(loc, "CALL_KW", 57, 2, 1)  # will pop more depending on arg, pushes ret val
def_op(loc, "SET_FUNCTION_ATTRIBUTE",106, 2, 1)  # pops func and attr val then pushes func back on stack
def_op(loc, "CONVERT_VALUE", 1, 1)
def_op(loc, "FORMAT_SIMPLE", 1, 1)
def_op(loc, "FORMAT_SPEC", 2, 1)

def_op(loc, "LOAD_CLOSURE", 258)  # psuedo-instruction


### update opinfo tables
# add new table "hasjump"
loc.update({"hasjump": [72, 77, 78, 79, 97, 98, 99, 100, 104, 256, 257]})
loc["hasjrel"] = loc["hasjump"]

# TODO continue updating tables

### update formatting
opcode_arg_fmt313 = opcode_312.opcode_arg_fmt12
opcode_extended_fmt = opcode_extended_fmt313 = opcode_312.opcode_extended_fmt312.copy()
from xdis.opcodes.opcode_312 import findlinestarts, parse_location_entries, format_CALL_INTRINSIC_1, format_CALL_INTRINSIC_2
opcode_arg_fmt = opcode_arg_fmt13 = opcode_312.opcode_arg_fmt312.copy()

update_pj3(globals(), loc)
finalize_opcodes(loc)
