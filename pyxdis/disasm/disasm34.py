#  Copyright (c) 2015-2016 by Rocky Bernstein
"""
Python 3.4 bytecode disassembler

This sets up opcodes Python's 3.4 and calls a generalized
scanner routine for Python 3.
"""

from pyxdis.disasm.disasm3 import Disassemble3

class Disassemble34(Disassemble3):

    def __init__(self):
        super(Disassemble3, self).__init__(3.4)


if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION == 3.4:
        from pyxdis.disasm.disasm3 import _test
        _test(PYTHON_VERSION)
    else:
        print("Need to be Python 3.4 to demo; I am %s." %
              PYTHON_VERSION)
