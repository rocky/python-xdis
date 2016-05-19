#  Copyright (c) 2016 by Rocky Bernstein
"""
Python 3.5 bytecode disassembler

This sets up opcodes Python's 3.5 and calls a generalized
disassemble routine for Python 3.
"""

from pyxdis.disasm.disasm3 import Disassemble3

class Disassemble35(Disassemble3):

    def __init__(self):
        super(Disassemble3, self).__init__(3.5)

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION == 3.5:
        from pyxdis.disasm.disasm3 import _test
        _test(PYTHON_VERSION)
    else:
        print("Need to be Python 3.5 to demo; I am %s." %
              PYTHON_VERSION)
