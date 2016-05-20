#  Copyright (c) 2015, 2016 by Rocky Bernstein

"""
Python 2 Generic bytecode disassembler

This overlaps various Python2's dis module, but it can be run from
Python versions other than the version running this code. Notably,
run from Python version 3 and we save instruction information.
"""

import dis
import pyxdis.disasm.dis2 as dis2

from collections import namedtuple
from array import array

from pyxdis.code import iscode
from pyxdis.instruction import Instruction
from pyxdis.disassemble import Disassemble
from pyxdis import PYTHON3

import pyxdis.disassemble as disasm

class Disassemble2(Disassemble):

    def __init__(self, version):
        super(Disassemble2, self).__init__(version)

    def disassemble(self, co, classname=None, code_objects={}):
        """
        Generic Python disassembly
        """
        # Container for instructions
        instructions = []

        self.code = array('B', co.co_code)

        bytecode = dis2.Bytecode(co, self.opc)

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

def _test(version):
    import inspect
    co = inspect.currentframe().f_code
    instructions = Disassemble2(version).disassemble(co)
    for i in instructions:
        print(i.format())

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if 2.0 <= PYTHON_VERSION < 3.0:
        from pyxdis import PYTHON_VERSION
        _test(PYTHON_VERSION)
    else:
        print("Need to be Python 2.0 upto Python 2.7 to demo; I am %s." %
              PYTHON_VERSION)
    pass
