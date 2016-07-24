import unittest
import dis
from xdis import PYTHON_VERSION, IS_PYPY
from xdis.opcodes import (opcode_23, opcode_24, opcode_25,
                          opcode_26, opcode_pypy26,
                          opcode_27, opcode_pypy27,
                          opcode_30, opcode_31,
                          opcode_32, opcode_pypy32, opcode_33,
                          opcode_34, opcode_35, opcode_36)

class TestOpcodes(unittest.TestCase):

    def test_basic(self):
        """Basic test that opcodes match native installed opcodes"""
        if PYTHON_VERSION == 2.3:
            return opcode_23
        elif PYTHON_VERSION == 2.4:
            return opcode_24
        elif PYTHON_VERSION == 2.5:
            return opcode_25
        elif PYTHON_VERSION == 2.6:
            if IS_PYPY:
                opc = opcode_pypy26
            else:
                opc = opcode_26
        elif PYTHON_VERSION == 2.7:
            if IS_PYPY:
                opc = opcode_pypy27
            else:
                opc = opcode_27
        elif PYTHON_VERSION == 3.0:
            opc = opcode_30
        elif PYTHON_VERSION == 3.1:
            opc = opcode_31
        elif PYTHON_VERSION == 3.2:
            if IS_PYPY:
                opc = opcode_pypy32
            else:
                opc = opcode_32
        elif PYTHON_VERSION == 3.3:
            opc = opcode_33
        elif PYTHON_VERSION == 3.4:
            opc = opcode_34
        elif PYTHON_VERSION == 3.5:
            opc = opcode_35
        elif PYTHON_VERSION == 3.6:
            opc = opcode_36
        else:
            self.assertFalse("Python version %s is not something I know about" % PYTHON_VERSION)
        # print(set(opc.opmap.items()) - set(dis.opmap.items()))
        # print(set(dis.opmap.items()) - set(opc.opmap.items()))

        self.assertTrue(all(item in opc.opmap.items() for item in dis.opmap.items()))
        self.assertTrue(all(item in dis.opmap.items() for item in opc.opmap.items()))

if __name__ == '__main__':
    unittest.main()
