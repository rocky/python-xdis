import os, sys, unittest
import dis
from pyxdis import PYTHON_VERSION
from pyxdis.opcodes import (opcode_25, opcode_26, opcode_27, \
                                opcode_30, opcode_31,
                                opcode_32, opcode_33, opcode_34, opcode_35)

class TestOpcodes(unittest.TestCase):

    def test_basic(self):
        """Basic test that opcodes match native installed opcodes"""
        if PYTHON_VERSION == 2.5:
            opc = opcode_25
        elif PYTHON_VERSION == 2.6:
            opc = opcode_26
        elif PYTHON_VERSION == 2.7:
            opc = opcode_27
        elif PYTHON_VERSION == 3.0:
            opc = opcode_30
        elif PYTHON_VERSION == 3.1:
            opc = opcode_31
        elif PYTHON_VERSION == 3.2:
            opc = opcode_32
        elif PYTHON_VERSION == 3.3:
            opc = opcode_33
        elif PYTHON_VERSION == 3.4:
            opc = opcode_34
        elif PYTHON_VERSION == 3.5:
            opc = opcode_35
        else:
            self.assertFalse("Python version %s is not something I know about" % PYTHON_VERSION)

        self.assertTrue(all(item in opc.opmap.items() for item in dis.opmap.items()))

if __name__ == '__main__':
    unittest.main()
