#  Copyright (c) 2015-2016 by Rocky Bernstein
"""
Python 3.0 bytecode disassembler

This sets up opcodes Python's 3.0 and calls a generalized
scanner routine for Python 3.
"""

from pyxdis.disasm.disasm3 import Disassemble3

class Disassemble30(Disassemble3):

    def __init__(self):
        super(Disassemble3, self).__init__(3.0)

    def disassemble(self, co, classname=None, code_objects={}):
        return self.disassemble3(co, classname, code_objects)

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION == 3.0:
        import inspect
        co = inspect.currentframe().f_code
        instructions = Disassemble32().disassemble(co)
        for i in instructions:
            print(i.format())
        pass
    else:
        print("Need to be Python 3.0 to demo; I am %s." %
              PYTHON_VERSION)
