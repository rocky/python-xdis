#  Copyright (c) 2015, 2016 by Rocky Bernstein

"""
Python 3 Generic bytecode disassembler

This overlaps various Python3's dis module, but it can be run from
Python versions other than the version running this code. Notably,
run from Python version 2 and we save instruction information.
"""

from __future__ import print_function

import dis
import pyxdis.disasm.dis3 as dis3

from collections import namedtuple
from array import array

from pyxdis.code import iscode
from pyxdis.instruction import Instruction
from pyxdis.disassemble import Disassemble
from pyxdis import PYTHON3


# Get all the opcodes into globals
import pyxdis.opcodes.opcode_33 as op3

globals().update(op3.opmap)

POP_JUMP_TF = (POP_JUMP_IF_TRUE, POP_JUMP_IF_FALSE)

import pyxdis.disassemble as disasm

class Disassemble3(Disassemble):

    def __init__(self, version):
        super(Disassemble3, self).__init__(version)

    def disassemble3(self, co, classname=None, code_objects={}):
        """
        Like disassemble3 but doesn't try to adjust any opcodes.
        """
        # Container for instructions
        instructions = []

        self.code = array('B', co.co_code)

        bytecode = dis3.Bytecode(co, self.opname)

        for inst in bytecode:
            pattr =  inst.argrepr
            opname = inst.opname
            instructions.append(
                Instruction(
                    type_ = opname,
                    attr = inst.argval,
                    pattr = pattr,
                    offset = inst.offset,
                    linestart = inst.starts_line,
                    )
                )
            pass
        return instructions

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION >= 3.0:
        import inspect
        co = inspect.currentframe().f_code
        from pyxdis import PYTHON_VERSION
        instructions = Disassemble3(PYTHON_VERSION).disassemble3(co)
        for i in instructions:
            print(i.format())
    else:
        print("Need to be Python 3.0 or greater to demo; I am %s." %
              PYTHON_VERSION)
    pass
