# Minimal tests for dis module
from __future__ import print_function

from xdis import PYTHON3, IS_PYPY

import six
import sys

if PYTHON3:
    from io import StringIO
else:
    from test.test_support import run_unittest
    from StringIO import StringIO

import unittest
import xdis.std as dis

def bug708901():
    for res in range(1,
                     10):
        pass

def bug1333982(x=[]):
    assert 0, ([s for s in x] +
              1)
    pass

if sys.version_info[0:2] == (2, 7):
    def _f(a):
        print(a)
        return 1

    dis_f = """\
%3d:           0 LOAD_GLOBAL               0 (print)
               3 LOAD_FAST                 0 (a)
               6 CALL_FUNCTION             1 (1 positional, 0 keyword pair)
               9 POP_TOP

%3d:          10 LOAD_CONST                1 (1)
              13 RETURN_VALUE

"""%(_f.func_code.co_firstlineno + 1,
         _f.func_code.co_firstlineno + 2)

    dis_bug708901 = """\
%3d:           0 SETUP_LOOP               23 (to 26)
               3 LOAD_GLOBAL               0 (range)
               6 LOAD_CONST                1 (1)

%3d:           9 LOAD_CONST                2 (10)
              12 CALL_FUNCTION             2 (2 positional, 0 keyword pair)
              15 GET_ITER
         >>   16 FOR_ITER                  6 (to 25)
              19 STORE_FAST                0 (res)

%3d:          22 JUMP_ABSOLUTE            16 (to 16)
         >>   25 POP_BLOCK
         >>   26 LOAD_CONST                0 (None)
              29 RETURN_VALUE

"""%(bug708901.func_code.co_firstlineno + 1,
     bug708901.func_code.co_firstlineno + 2,
     bug708901.func_code.co_firstlineno + 3)


    dis_bug708901pypy = """\
%3d:           0 SETUP_LOOP               23 (to 26)
               3 LOAD_GLOBAL               0 (range)
               6 LOAD_CONST                1 (1)

%3d:           9 LOAD_CONST                2 (10)
              12 CALL_FUNCTION             2 (2 positional, 0 keyword pair)
              15 GET_ITER
         >>   16 FOR_ITER                  6 (to 25)
              19 STORE_FAST                0 (res)

%3d:          22 JUMP_ABSOLUTE            16 (to 16)
         >>   25 POP_BLOCK
         >>   26 LOAD_CONST                0 (None)
              29 RETURN_VALUE

"""%(bug708901.func_code.co_firstlineno + 1,
     bug708901.func_code.co_firstlineno + 2,
     bug708901.func_code.co_firstlineno + 3)


    dis_bug1333982 = """\
%3d:          0 LOAD_CONST                1 (0)
              3 POP_JUMP_IF_TRUE         41 (to 41)
              6 LOAD_GLOBAL               0 (AssertionError)
              9 BUILD_LIST                0
             12 LOAD_FAST                 0 (x)
             15 GET_ITER
        >>   16 FOR_ITER                 12 (to 31)
             19 STORE_FAST                1 (s)
             22 LOAD_FAST                 1 (s)
             25 LIST_APPEND               2
             28 JUMP_ABSOLUTE            16 (to 16)

%3d:    >>   31 LOAD_CONST                2 (1)
             34 BINARY_ADD
             35 CALL_FUNCTION             1 (1 positional, 0 keyword pair)
             38 RAISE_VARARGS             1

%3d:    >>   41 LOAD_CONST                0 (None)
             44 RETURN_VALUE

"""%(bug1333982.func_code.co_firstlineno + 1,
     bug1333982.func_code.co_firstlineno + 2,
     bug1333982.func_code.co_firstlineno + 3)

    _BIG_LINENO_FORMAT = """\
%3d:           0 LOAD_GLOBAL               0 (spam)
               3 POP_TOP
               4 LOAD_CONST                0 (None)
               7 RETURN_VALUE

"""

    class DisTests(unittest.TestCase):
        def do_disassembly_test(self, func, expected):
            s = StringIO()
            save_stdout = sys.stdout
            sys.stdout = s
            dis.dis(func)
            sys.stdout = save_stdout
            got = s.getvalue()
            # Trim trailing blanks (if any).
            lines = got.split('\n')
            # lines = [line.rstrip() for line in lines]
            expected = expected.split("\n")
            import difflib
            if expected != lines:
                self.fail(
                    "events did not match expectation:\n" +
                    "\n".join(difflib.ndiff(expected,
                                            lines)))

        def test_opmap(self):
            self.assertEqual(dis.opmap["STOP_CODE"], 0)
            self.assertIn(dis.opmap["LOAD_CONST"], dis.hasconst)
            self.assertIn(dis.opmap["STORE_NAME"], dis.hasname)

        def test_opname(self):
            opname = dis.opname
            opmap = dis.opmap
            self.assertEqual(opname[opmap["LOAD_FAST"]], "LOAD_FAST")

        def test_boundaries(self):
            opmap = dis.opmap
            self.assertEqual(opmap["EXTENDED_ARG"], dis.EXTENDED_ARG)
            self.assertEqual(opmap["STORE_NAME"], dis.HAVE_ARGUMENT)

        def test_dis(self):
            self.do_disassembly_test(_f, dis_f)

        def test_bug_708901(self):
            if IS_PYPY:
                self.do_disassembly_test(bug708901, dis_bug708901pypy)
            else:
                self.do_disassembly_test(bug708901, dis_bug708901)

        def test_bug_1333982(self):
            # This one is checking bytecodes generated for an `assert` statement,
            # so fails if the tests are run with -O.  Skip this test then.
            if False:
                self.do_disassembly_test(bug1333982, dis_bug1333982)
            else:
                self.skipTest('need asserts, run without -O')

        def test_big_linenos(self):
            def func(count):
                namespace = {}
                func = "def foo():\n " + "".join(["\n "] * count + ["spam\n"]
                )
                exec_fn = six.__dict__['exec_']
                exec_fn(func, namespace)
                return namespace['foo']

            # Test all small ranges
            for i in range(1, 300):
                expected = _BIG_LINENO_FORMAT % (i + 2)
                self.do_disassembly_test(func(i), expected)

            # Test some larger ranges too
            for i in range(300, 5000, 10):
                expected = _BIG_LINENO_FORMAT % (i + 2)
                self.do_disassembly_test(func(i), expected)

    def test_main():
        run_unittest(DisTests)


if __name__ == "__main__":
    test_main()
