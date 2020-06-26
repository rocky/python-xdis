# Minimal tests for from the Python 2.7 dis module test

import unittest

import sys

PY32 = sys.version_info[0:2] >= (3, 2)
PY36 = sys.version_info[0:2] >= (3, 6)
USE_WORDCODE = PY36

if USE_WORDCODE:
    from xdis.opcodes import opcode_36 as opc
else:
    from xdis.opcodes import opcode_27 as opc

from xdis.bytecode import Bytecode

_BIG_LINENO_FORMAT_36 = """\
%4d:           0 LOAD_GLOBAL          (spam)
               2 POP_TOP
               4 LOAD_CONST           (None)
               6 RETURN_VALUE
"""

_BIG_LINENO_FORMAT = """\
%3d:           0 LOAD_GLOBAL          (spam)
               3 POP_TOP
               4 LOAD_CONST           (None)
               7 RETURN_VALUE
"""

class DisTests(unittest.TestCase):

    def do_disassembly(self, func, expected):

        co = func.func_code
        bytecode = Bytecode(co, opc)
        got = bytecode.dis()

        # Trim trailing blanks (if any).
        lines = got.split('\n')
        lines = [line.rstrip() for line in lines]
        expected = expected.split("\n")
        import difflib
        if expected != lines:
            self.fail(
                "events did not match expectation:\n" +
                "\n".join(difflib.ndiff(expected,
                                        lines)))

    def test_opmap(self):
        # STOP_CODE removed from python 3.2
        if not PY32:
            self.assertEqual(opc.opmap["STOP_CODE"], 0)
        self.assertTrue(opc.opmap["LOAD_CONST"] in opc.CONST_OPS)
        self.assertTrue(opc.opmap["STORE_NAME"] in opc.NAME_OPS)

    def test_opname(self):
        self.assertEqual(opc.opname[opc.opmap["LOAD_FAST"]], "LOAD_FAST")

    def test_boundaries(self):
        self.assertEqual(opc.opmap["EXTENDED_ARG"], opc.EXTENDED_ARG)
        self.assertEqual(opc.opmap["STORE_NAME"], opc.HAVE_ARGUMENT)

    def test_big_linenos(self):
        def func(count):
            namespace = {}
            func = "def foo():\n " + "".join(["\n "] * count + ["spam\n"])
            exec(func, namespace)
            return namespace['foo']

        # Test all small ranges
        if PY36:
            big_lineno_format = _BIG_LINENO_FORMAT_36
        else:
            big_lineno_format = _BIG_LINENO_FORMAT
        for i in range(1, 127):
            expected = big_lineno_format % (i + 2)
            self.do_disassembly(func(i), expected)

        # Test some larger ranges too
        # for i in range(127, 5000, 10):
        #     expected = big_lineno_format % i
        #     self.do_disassembly(func(i), expected)

if __name__ == "__main__":
    unittest.main()
