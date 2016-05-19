#  Copyright (c) 2015-2016 by Rocky Bernstein
"""
Python 3.2 bytecode disassembler

This sets up opcodes Python's 3.2 and calls a generalized
scanner routine for Python 3.
"""

from pyxdis.disasm.disasm3 import Disassemble3

class Disassemble32(Disassemble3):

    def __init__(self):
        super(Disassemble3, self).__init__(3.2)

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION == 3.2:
        from pyxdis.disasm.disasm3 import _test
        _test(PYTHON_VERSION)
    else:
        print("Need to be Python 3.2 to demo; I am %s." %
              PYTHON_VERSION)
