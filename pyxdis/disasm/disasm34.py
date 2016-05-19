#  Copyright (c) 2015-2016 by Rocky Bernstein
"""
Python 3.4 bytecode disassembler

This sets up opcodes Python's 3.4 and calls a generalized
scanner routine for Python 3.
"""

from pyxdis.disasm.disasm3 import Disassemble3

class Disassemble34(Disassemble3):

    def __init__(self):
        super(Disassembe3, self).__init__(3.4)

    def disassemble(self, co, classname=None, code_objects={}):
        return self.disassemble3(co, classname, code_objects)

if __name__ == "__main__":
    from uncompyle6 import PYTHON_VERSION
    if PYTHON_VERSION == 3.2:
        import inspect
        co = inspect.currentframe().f_code
        instructions = Diassemble34().disassemble(co)
        for i in instructions:
            print(i.format())
        pass
    else:
        print("Need to be Python 3.2 to demo; I am %s." %
              PYTHON_VERSION)
