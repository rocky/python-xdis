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

    def disassemble(self, co, classname=None, code_objects={}):
        return self.disassemble3(co, classname, code_objects)

if __name__ == "__main__":
    from pyxdis import PYTHON_VERSION
    if PYTHON_VERSION == 3.5:
        import inspect
        co = inspect.currentframe().f_code
        instructions = Disassemble35().disassemble(co)
        for i in instructions:
            print(i.format())
        pass
    else:
        print("Need to be Python 3.5 to demo; I am %s." %
              PYTHON_VERSION)
