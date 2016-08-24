# Minimal tests for from the Python 2.7 dis module test
from __future__ import print_function

import unittest

from xdis.opcodes import opcode_27 as opc
from xdis.bytecode import Bytecode
from xdis import PYTHON_VERSION

def _f(a):
    print(a)
    return 1

dis_f = """\
 %-4d         0 LOAD_FAST                0 (a)
              3 PRINT_ITEM
              4 PRINT_NEWLINE

 %-4d         5 LOAD_CONST               1 (1)
              8 RETURN_VALUE
"""%(_f.func_code.co_firstlineno + 1,
     _f.func_code.co_firstlineno + 2)


def bug708901():
    for res in range(1,
                     10):
        pass

dis_bug708901 = """\
 %-4d         0 SETUP_LOOP              23 (to 26)
              3 LOAD_GLOBAL              0 (range)
              6 LOAD_CONST               1 (1)

 %-4d         9 LOAD_CONST               2 (10)
             12 CALL_FUNCTION            2 (2 positional, 0 keyword pair)
             15 GET_ITER
        >>   16 FOR_ITER                 6 (to 25)
             19 STORE_FAST               0 (res)

 %-4d        22 JUMP_ABSOLUTE           16 (to 16)
        >>   25 POP_BLOCK
        >>   26 LOAD_CONST               0 (None)
             29 RETURN_VALUE
"""%(bug708901.func_code.co_firstlineno + 1,
     bug708901.func_code.co_firstlineno + 2,
     bug708901.func_code.co_firstlineno + 3)


def bug1333982(x=[]):
    assert 0, ([s for s in x] +
              1)
    pass

dis_bug1333982 = """\
 %-4d         0 LOAD_CONST               1 (0)
              3 POP_JUMP_IF_TRUE        41 (to 41)
              6 LOAD_GLOBAL              0 (AssertionError)
              9 BUILD_LIST               0
             12 LOAD_FAST                0 (x)
             15 GET_ITER
        >>   16 FOR_ITER                12 (to 31)
             19 STORE_FAST               1 (s)
             22 LOAD_FAST                1 (s)
             25 LIST_APPEND              2
             28 JUMP_ABSOLUTE           16 (to 16)

 %-4d   >>   31 LOAD_CONST               2 (1)
             34 BINARY_ADD
             35 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             38 RAISE_VARARGS            1

 %-4d   >>   41 LOAD_CONST               0 (None)
             44 RETURN_VALUE
"""%(bug1333982.func_code.co_firstlineno + 1,
     bug1333982.func_code.co_firstlineno + 2,
     bug1333982.func_code.co_firstlineno + 3)

_BIG_LINENO_FORMAT = """\
%3d           0 LOAD_GLOBAL              0 (spam)
              3 POP_TOP
              4 LOAD_CONST               0 (None)
              7 RETURN_VALUE
"""

class DisTests(unittest.TestCase):

    def do_disassembly_test(self, func, expected):
        if PYTHON_VERSION != 2.7:
            print('need Python 2.7')
            return

        co = func.__code__
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
            pass
        return

    def test_dis(self):
        self.do_disassembly_test(_f, dis_f)

    def test_bug_708901(self):
        self.do_disassembly_test(bug708901, dis_bug708901)

    def test_bug_1333982(self):
        # This one is checking bytecodes generated for an `assert` statement,
        # so fails if the tests are run with -O.  Skip this test then.
        if __debug__:
            self.do_disassembly_test(bug1333982, dis_bug1333982)
        else:
            print('need asserts, run without -O')
            pass
        return
    pass

if __name__ == "__main__":
    unittest.main()
