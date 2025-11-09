"""
CPython 3.14 bytecode opcodes. THIS IS INCOMPLETE.
"""

import xdis.opcodes.opcode_313 as opcode_313
from xdis.opcodes.base import (  # noqa
    cpython_implementation as python_implementation,
    finalize_opcodes,
    init_opdata,
    update_pj3,
)

version_tuple = (3, 14)

loc = locals()

init_opdata(loc, opcode_313, version_tuple)

### update formatting
opcode_arg_fmt = opcode_arg_fmt314 = opcode_313.opcode_arg_fmt313.copy()

opcode_extended_fmt = opcode_extended_fmt313 = (opcode_313.opcode_extended_fmt313,)
findlinestarts = opcode_313.findlinestarts_313

update_pj3(globals(), loc)
finalize_opcodes(loc)
