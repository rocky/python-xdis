# Minimal tests for dis module

import unittest
import sys
import xdis.std as dis
import io
import re
import types
import contextlib

class _C:
    def __init__(self, x):
        self.x = x == 1

if sys.version_info[0:2] == (3, 4):
    from test.bytecode_helper import BytecodeTestCase
    from test.support import captured_stdout

    def get_tb():
        def _error():
            try:
                1 / 0
            except Exception as e:
                tb = e.__traceback__
            return tb

        tb = _error()
        while tb.tb_next:
            tb = tb.tb_next
        return tb

    TRACEBACK_CODE = get_tb().tb_frame.f_code

    dis_c_instance_method = """\
 %4d:         0 LOAD_FAST                 1 (x)
              3 LOAD_CONST                1 (1)
              6 COMPARE_OP                2 (==)
              9 LOAD_FAST                 0 (self)
             12 STORE_ATTR                0 (x)
             15 LOAD_CONST                0 (None)
             18 RETURN_VALUE

""" % (_C.__init__.__code__.co_firstlineno + 1,)

    dis_c_instance_method_bytes = """\
          0 LOAD_FAST            1 (1)
          3 LOAD_CONST           1 (1)
          6 COMPARE_OP           2 (==)
          9 LOAD_FAST            0 (0)
         12 STORE_ATTR           0 (0)
         15 LOAD_CONST           0 (0)
         18 RETURN_VALUE

"""

    def _f(a):
        print(a)
        return 1

    dis_f = """\
%3d:           0 LOAD_GLOBAL               0 (print)
                3 LOAD_FAST                 0 (a)
                6 CALL_FUNCTION             1 (1 positional, 0 keyword pair)
                9 POP_TOP

%3d:           10 LOAD_CONST                1 (1)
               13 RETURN_VALUE

""" % (_f.__code__.co_firstlineno + 1,
       _f.__code__.co_firstlineno + 2)


    dis_f_co_code = """\
 57:           0 LOAD_GLOBAL               0 (print)
                3 LOAD_FAST                 0 (a)
                6 CALL_FUNCTION             1 (1 positional, 0 keyword pair)
                9 POP_TOP

 58:          10 LOAD_CONST                1 (1)
               13 RETURN_VALUE

"""


    def bug708901():
        for res in range(1,
                         10):
            pass
        return

    dis_bug708901 = """\
%4d:         0 SETUP_LOOP               23 (to 26)
             3 LOAD_GLOBAL               0 (range)
             6 LOAD_CONST                1 (1)

%4d:         9 LOAD_CONST                2 (10)
            12 CALL_FUNCTION             2 (2 positional, 0 keyword pair)
            15 GET_ITER
       >>   16 FOR_ITER                  6 (to 25)
            19 STORE_FAST                0 (res)

%4d:        22 JUMP_ABSOLUTE            16 (to 16)
       >>   25 POP_BLOCK
       >>   26 LOAD_CONST                0 (None)
            29 RETURN_VALUE

""" % (bug708901.__code__.co_firstlineno + 1,
       bug708901.__code__.co_firstlineno + 2,
       bug708901.__code__.co_firstlineno + 3)


    def bug1333982(x=[]):
        assert 0, ([s for s in x] +
                  1)
        pass

    dis_bug1333982 = """\
%4d:         0 LOAD_CONST                1 (0)
             3 POP_JUMP_IF_TRUE         92 (to 92)
             6 LOAD_GLOBAL               0 (AssertionError)
             9 LOAD_CONST                2 (<code object <listcomp> at 0x..., file "%s", line %d>)
            12 LOAD_CONST                3 ('bug1333982.<locals>.<listcomp>')
            15 MAKE_FUNCTION             0 (0 positional, 0 name and default, 0 annotations)
            18 LOAD_FAST                 0 (x)
            21 GET_ITER
            22 CALL_FUNCTION             1 (1 positional, 0 keyword pair)

%4d:        25 LOAD_CONST                4 (1)
            28 BINARY_ADD
            29 CALL_FUNCTION             1 (1 positional, 0 keyword pair)
            32 RAISE_VARARGS             1

%4d:   >>   35 LOAD_CONST                0 (None)
            38 RETURN_VALUE

""" % (bug1333982.__code__.co_firstlineno + 1,
       __file__,
       bug1333982.__code__.co_firstlineno + 1,
       bug1333982.__code__.co_firstlineno + 2,
       bug1333982.__code__.co_firstlineno + 3)

    _BIG_LINENO_FORMAT = """\
%3d:           0 LOAD_GLOBAL               0 (spam)
               3 POP_TOP
               4 LOAD_CONST                0 (None)
               7 RETURN_VALUE

"""

    dis_module_expected_results = """\
Disassembly of f:
  4           0 LOAD_CONST                0 (None)
              3 RETURN_VALUE

Disassembly of g:
  5           0 LOAD_CONST                0 (None)
              3 RETURN_VALUE

"""

    expr_str = "x + 1"

    dis_expr_str = """\
  1:           0 LOAD_NAME                 0 (x)
               3 LOAD_CONST                0 (1)
               6 BINARY_ADD
               7 RETURN_VALUE

"""

    simple_stmt_str = "x = x + 1"

    dis_simple_stmt_str = """\
  1:           0 LOAD_NAME                 0 (x)
               3 LOAD_CONST                0 (1)
               6 BINARY_ADD
               7 STORE_NAME                0 (x)
              10 LOAD_CONST                1 (None)
              13 RETURN_VALUE

"""

    compound_stmt_str = """\
x = 0
while 1:
    x += 1"""
    # Trailing newline has been deliberately omitted

    dis_compound_stmt_str = """\
  1           0 LOAD_CONST                0 (0)
              3 STORE_NAME                0 (x)

  2           6 SETUP_LOOP               13 (to 22)

  3     >>    9 LOAD_NAME                 0 (x)
             12 LOAD_CONST                1 (1)
             15 INPLACE_ADD
             16 STORE_NAME                0 (x)
             19 JUMP_ABSOLUTE             9 (to 9)
        >>   22 LOAD_CONST                2 (None)
             25 RETURN_VALUE

"""

    dis_traceback = """\
 %-4d         0 SETUP_EXCEPT             12 (to 15)

 %-4d         3 LOAD_CONST                1 (1)
              6 LOAD_CONST                2 (0)
    -->       9 BINARY_TRUE_DIVIDE
             10 POP_TOP
             11 POP_BLOCK
             12 JUMP_FORWARD             46 (to 61)

 %-4d   >>   15 DUP_TOP
             16 LOAD_GLOBAL               0 (Exception)
             19 COMPARE_OP               10 (exception match)
             22 POP_JUMP_IF_FALSE        60
             25 POP_TOP
             26 STORE_FAST                0 (e)
             29 POP_TOP
             30 SETUP_FINALLY            14 (to 47)

 %-4d        33 LOAD_FAST                 0 (e)
             36 LOAD_ATTR                 1 (__traceback__)
             39 STORE_FAST                1 (tb)
             42 POP_BLOCK
             43 POP_EXCEPT
             44 LOAD_CONST                0 (None)
        >>   47 LOAD_CONST                0 (None)
             50 STORE_FAST                0 (e)
             53 DELETE_FAST               0 (e)
             56 END_FINALLY
             57 JUMP_FORWARD              1 (to 61)
        >>   60 END_FINALLY

 %-4d   >>   61 LOAD_FAST                1 (tb)
             64 RETURN_VALUE

""" % (TRACEBACK_CODE.co_firstlineno + 1,
       TRACEBACK_CODE.co_firstlineno + 2,
       TRACEBACK_CODE.co_firstlineno + 3,
       TRACEBACK_CODE.co_firstlineno + 4,
       TRACEBACK_CODE.co_firstlineno + 5)

    class DisTests(unittest.TestCase):


        def get_disassembly(self, func, lasti=-1, wrapper=True):
            # We want to test the default printing behaviour, not the file arg
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                if wrapper:
                    dis.dis(func)
                else:
                    dis.disassemble(func, lasti)
            return output.getvalue()

        def get_disassemble_as_string(self, func, lasti=-1):
            return self.get_disassembly(func, lasti, False)

        def strip_addresses(self, text):
            return re.sub(r'\b0x[0-9A-Fa-f]+\b', '0x...', text)

        def dis_disassembly34(self, func, expected):
            got = self.get_disassembly(func)
            if got != expected:
                got = self.strip_addresses(got)
            self.assertEqual(got, expected)

        def test_opmap(self):
            self.assertEqual(dis.opmap["NOP"], 9)
            self.assertIn(dis.opmap["LOAD_CONST"], dis.hasconst)
            self.assertIn(dis.opmap["STORE_NAME"], dis.hasname)

        def test_opname(self):
            self.assertEqual(dis.opname[dis.opmap["LOAD_FAST"]], "LOAD_FAST")

        def test_boundaries(self):
            self.assertEqual(dis.opmap["EXTENDED_ARG"], dis.EXTENDED_ARG)
            self.assertEqual(dis.opmap["STORE_NAME"], dis.HAVE_ARGUMENT)

        # def test_dis(self):
        #     self.dis_disassembly34(_f, dis_f)

        def test_bug_708901(self):
            self.skipTest('fix 708901')
            self.dis_disassembly34(bug708901, dis_bug708901)

        def test_bug_1333982(self):
            # This one is checking bytecodes generated for an `assert` statement,
            # so fails if the tests are run with -O.  Skip this test then.
            if not False:
                self.skipTest('need asserts, run without -O')

            self.dis_disassembly34(bug1333982, dis_bug1333982)

        def test_big_linenos(self):
            def func(count):
                namespace = {}
                func = "def foo():\n " + "".join(["\n "] * count + ["spam\n"])
                exec(func, namespace)
                return namespace['foo']

            # Test all small ranges
            for i in range(1, 300):
                expected = _BIG_LINENO_FORMAT % (i + 2)
                self.dis_disassembly34(func(i), expected)

            # Test some larger ranges too
            for i in range(300, 5000, 10):
                expected = _BIG_LINENO_FORMAT % (i + 2)
                self.dis_disassembly34(func(i), expected)

            self.skipTest('Add ability to disassemble module')
            # from test import dis_module
            # self.dis_disassembly34(dis_module, dis_module_expected_results)

        def test_disassemble_str(self):
            self.dis_disassembly34(expr_str, dis_expr_str)
            self.dis_disassembly34(simple_stmt_str, dis_simple_stmt_str)
            self.skipTest('Fix dis_compund_stmt_str')
            # self.dis_disassembly34(compound_stmt_str, dis_compound_stmt_str)

        def test_disassemble_bytes(self):
            self.skipTest('Fix output')
            self.dis_disassembly34(_f.__code__, dis_f_co_code)

        def test_disassemble_method(self):
            self.skipTest('Fix output')
            self.dis_disassembly34(_C(1).__init__, dis_c_instance_method)

        def test_disassemble_method_bytes(self):
            self.skipTest('Add ability to disassemble bytes')
            # method_bytecode = _C(1).__init__.__code__.co_code
            # self.dis_disassembly34(method_bytecode, dis_c_instance_method_bytes)

        def test_dis_none(self):
            try:
                del sys.last_traceback
            except AttributeError:
                pass
            self.assertRaises(TypeError, dis.dis, None)

        def test_dis_traceback(self):
            self.skipTest('Fix up ability to disassemble straceback')
            return
            try:
                del sys.last_traceback
            except AttributeError:
                pass

            try:
                1/0
            except Exception as e:
                tb = e.__traceback__
                sys.last_traceback = tb

            tb_dis = self.get_disassemble_as_string(tb.tb_frame.f_code, tb.tb_lasti)
            self.dis_disassembly34(None, tb_dis)

        def test_dis_object(self):
            self.assertRaises(TypeError, dis.dis, object())

    class DisWithFileTests(DisTests):

        # Run the tests again, using the file arg instead of print
        def get_disassembly(self, func, lasti=-1, wrapper=True):
            output = io.StringIO()
            if wrapper:
                dis.dis(func, file=output)
            else:
                dis.disassemble(func, lasti, file=output)
            return output.getvalue()



    code_info_code_info = """\
    Method Name:              code_info
    Filename:          (.*)
    Argument count:    1
    Kw-only arguments: 0
    Number of locals:  1
    Stack size:        3
    Flags:             OPTIMIZED, NEWLOCALS, NOFREE
    Constants:
       0: %r
    Names:
       0: _format_code_info
       1: _get_code_object
    Variable names:
       0: x""" % (('Formatted details of methods, functions, or code.',)
                  if sys.flags.optimize < 2 else (None,))

    # @staticmethod
    # def tricky(x, y, z=True, *args, c, d, e=[], **kwds):
    #     def f(c=c):
    #         print(x, y, z, c, d, e, f)
    #     yield x, y, z, c, d, e, f

    code_info_tricky = """\
    Method Name:              tricky
    Filename:          (.*)
    Argument count:    3
    Kw-only arguments: 3
    Number of locals:  8
    Stack size:        7
    Flags:             OPTIMIZED, NEWLOCALS, VARARGS, VARKEYWORDS, GENERATOR
    Constants:
       0: None
       1: <code object f at (.*), file "(.*)", line (.*)>
       2: 'tricky.<locals>.f'
    Variable names:
       0: x
       1: y
       2: z
       3: c
       4: d
       5: e
       6: args
       7: kwds
    Cell variables:
       0: [edfxyz]
       1: [edfxyz]
       2: [edfxyz]
       3: [edfxyz]
       4: [edfxyz]
       5: [edfxyz]"""
    # NOTE: the order of the cell variables above depends on dictionary order!

    # co_tricky_nested_f = tricky.__func__.__code__.co_consts[1]

    code_info_tricky_nested_f = """\
    Method Name:              f
    Filename:          (.*)
    Argument count:    1
    Kw-only arguments: 0
    Number of locals:  1
    Stack size:        8
    Flags:             OPTIMIZED, NEWLOCALS, NESTED
    Constants:
       0: None
    Names:
       0: print
    Variable names:
       0: c
    Free variables:
       0: [edfxyz]
       1: [edfxyz]
       2: [edfxyz]
       3: [edfxyz]
       4: [edfxyz]
       5: [edfxyz]"""

    code_info_expr_str = """\
    Name:              <module>
    Filename:          <disassembly>
    Argument count:    0
    Kw-only arguments: 0
    Number of locals:  0
    Stack size:        2
    Flags:             NOFREE
    Constants:
       0: 1
    Names:
       0: x"""

    code_info_simple_stmt_str = """\
    Name:              <module>
    Filename:          <disassembly>
    Argument count:    0
    Kw-only arguments: 0
    Number of locals:  0
    Stack size:        2
    Flags:             NOFREE
    Constants:
       0: 1
       1: None
    Names:
       0: x"""

    code_info_compound_stmt_str = """\
    Name:              <module>
    Filename:          <disassembly>
    Argument count:    0
    Kw-only arguments: 0
    Number of locals:  0
    Stack size:        2
    Flags:             NOFREE
    Constants:
       0: 0
       1: 1
       2: None
    Names:
       0: x"""

    class CodeInfoTests(unittest.TestCase):
        test_pairs = [
          # (dis.code_info, code_info_code_info),
          # (tricky, code_info_tricky),
          # (co_tricky_nested_f, code_info_tricky_nested_f),
          # (expr_str, code_info_expr_str),
          # (simple_stmt_str, code_info_simple_stmt_str),
          # (compound_stmt_str, code_info_compound_stmt_str),
        ]

        def test_code_info(self):
            self.skipTest('Reconcile differences in format')
            return
            self.maxDiff = 1000
            for x, expected in self.test_pairs:
                self.assertRegex(dis.code_info(x), expected)

        def test_show_code(self):
            self.maxDiff = 1000
            for x, expected in self.test_pairs:
                with captured_stdout() as output:
                    dis.show_code(x)
                self.assertRegex(output.getvalue(), expected+"\n")

        def test_code_info_object(self):
            self.assertRaises(TypeError, dis.code_info, object())

        def test_pretty_flags_no_flags(self):
            self.assertEqual(dis.pretty_flags(0), '0x00000000 (0x0)')


    # Fodder for instruction introspection tests
    #   Editing any of these may require recalculating the expected output
    def outer(a=1, b=2):
        def f(c=3, d=4):
            def inner(e=5, f=6):
                print(a, b, c, d, e, f)
            print(a, b, c, d)
            return inner
        print(a, b, '', 1, [], {}, "Hello world!")
        return f

    def jumpy():
        # This won't actually run (but that's OK, we only disassemble it)
        for i in range(10):
            print(i)
            if i < 4:
                continue
            if i > 6:
                break
        else:
            print("I can haz else clause?")
        while i:
            print(i)
            i -= 1
            if i > 6:
                continue
            if i < 4:
                break
        else:
            print("Who let lolcatz into this test suite?")
        try:
            1 / 0
        except ZeroDivisionError:
            print("Here we go, here we go, here we go...")
        else:
            with i as dodgy:
                print("Never reach this")
        finally:
            print("OK, now we're done")

    # End fodder for opinfo generation tests
    expected_outer_line = 1
    _line_offset = outer.__code__.co_firstlineno - 1
    code_object_f = outer.__code__.co_consts[3]
    expected_f_line = code_object_f.co_firstlineno - _line_offset
    code_object_inner = code_object_f.co_consts[3]
    expected_inner_line = code_object_inner.co_firstlineno - _line_offset
    expected_jumpy_line = 1

    # The following lines are useful to regenerate the expected results after
    # either the fodder is modified or the bytecode generation changes
    # After regeneration, update the references to code_object_f and
    # code_object_inner before rerunning the tests

    # _instructions = dis.get_instructions(outer, first_line=expected_outer_line)
    # print('expected_opinfo_outer = [\n  ',
    #       ',\n  '.join(map(str, _instructions)), ',\n]', sep='')
    # _instructions = dis.get_instructions(outer(), first_line=expected_outer_line)
    # print('expected_opinfo_f = [\n  ',
    #       ',\n  '.join(map(str, _instructions)), ',\n]', sep='')
    # _instructions = dis.get_instructions(outer()(), first_line=expected_outer_line)
    # print('expected_opinfo_inner = [\n  ',
    #       ',\n  '.join(map(str, _instructions)), ',\n]', sep='')
    # _instructions = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
    # print('expected_opinfo_jumpy = [\n  ',
    #       ',\n  '.join(map(str, _instructions)), ',\n]', sep='')


    Instruction = dis.Instruction
    expected_opinfo_outer = [
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=1, argval=3, argrepr='3', has_arg=True, offset=0, starts_line=2, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=2, argval=4, argrepr='4', has_arg=True, offset=3, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=0, argval='a', argrepr='a', has_arg=True, offset=6, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=1, argval='b', argrepr='b', has_arg=True, offset=9, starts_line=None, is_jump_target=False),
      Instruction(opname='BUILD_TUPLE', opcode=102, optype='vargs', inst_size=3, arg=2, argval=2, argrepr='', has_arg=True, offset=12, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=3, argval=code_object_f, argrepr=repr(code_object_f), has_arg=True, offset=15, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=4, argval='outer.<locals>.f', argrepr="'outer.<locals>.f'", has_arg=True, offset=18, starts_line=None, is_jump_target=False),
      Instruction(opname='MAKE_CLOSURE', opcode=134, optype=None, inst_size=3, arg=2, argval=2, argrepr='', has_arg=True, offset=21, starts_line=None, is_jump_target=False),
      Instruction(opname='STORE_FAST', opcode=125, optype='local', inst_size=3, arg=2, argval='f', argrepr='f', has_arg=True, offset=24, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=0, argval='print', argrepr='print', has_arg=True, offset=27, starts_line=7, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=0, argval='a', argrepr='a', has_arg=True, offset=30, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=1, argval='b', argrepr='b', has_arg=True, offset=33, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=5, argval='', argrepr="''", has_arg=True, offset=36, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=6, argval=1, argrepr='1', has_arg=True, offset=39, starts_line=None, is_jump_target=False),
      Instruction(opname='BUILD_LIST', opcode=103, optype='vargs', inst_size=3, arg=0, argval=0, argrepr='', has_arg=True, offset=42, starts_line=None, is_jump_target=False),
      Instruction(opname='BUILD_MAP', opcode=105, optype='vargs', inst_size=3, arg=0, argval=0, argrepr='', has_arg=True, offset=45, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=7, argval='Hello world!', argrepr="'Hello world!'", has_arg=True, offset=48, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=7, argval=7, argrepr='7 positional, 0 keyword pair', has_arg=True, offset=51, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=54, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=2, argval='f', argrepr='f', has_arg=True, offset=55, starts_line=8, is_jump_target=False),
      Instruction(opname='RETURN_VALUE', opcode=83, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=58, starts_line=None, is_jump_target=False),
    ]

    expected_opinfo_f = [
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=1, argval=5, argrepr='5', has_arg=True, offset=0, starts_line=3, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=2, argval=6, argrepr='6', has_arg=True, offset=3, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=2, argval='a', argrepr='a', has_arg=True, offset=6, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=3, argval='b', argrepr='b', has_arg=True, offset=9, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=0, argval='c', argrepr='c', has_arg=True, offset=12, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CLOSURE', opcode=135, optype='free', inst_size=3, arg=1, argval='d', argrepr='d', has_arg=True, offset=15, starts_line=None, is_jump_target=False),
      Instruction(opname='BUILD_TUPLE', opcode=102, optype='vargs', inst_size=3, arg=4, argval=4, argrepr='', has_arg=True, offset=18, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=3, argval=code_object_inner, argrepr=repr(code_object_inner), has_arg=True, offset=21, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=4, argval='outer.<locals>.f.<locals>.inner', argrepr="'outer.<locals>.f.<locals>.inner'", has_arg=True, offset=24, starts_line=None, is_jump_target=False),
      Instruction(opname='MAKE_CLOSURE', opcode=134, optype=None, inst_size=3, arg=2, argval=2, argrepr='', has_arg=True, offset=27, starts_line=None, is_jump_target=False),
      Instruction(opname='STORE_FAST', opcode=125, optype='local', inst_size=3, arg=2, argval='inner', argrepr='inner', has_arg=True, offset=30, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=0, argval='print', argrepr='print', has_arg=True, offset=33, starts_line=5, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=2, argval='a', argrepr='a', has_arg=True, offset=36, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=3, argval='b', argrepr='b', has_arg=True, offset=39, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=0, argval='c', argrepr='c', has_arg=True, offset=42, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=1, argval='d', argrepr='d', has_arg=True, offset=45, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=4, argval=4, argrepr='4 positional, 0 keyword pair', has_arg=True, offset=48, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=51, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=2, argval='inner', argrepr='inner', has_arg=True, offset=52, starts_line=6, is_jump_target=False),
      Instruction(opname='RETURN_VALUE', opcode=83, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=55, starts_line=None, is_jump_target=False),
    ]

    expected_opinfo_inner = [
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=0, argval='print', argrepr='print', has_arg=True, offset=0, starts_line=4, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=0, argval='a', argrepr='a', has_arg=True, offset=3, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=1, argval='b', argrepr='b', has_arg=True, offset=6, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=2, argval='c', argrepr='c', has_arg=True, offset=9, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_DEREF', opcode=136, optype='free', inst_size=3, arg=3, argval='d', argrepr='d', has_arg=True, offset=12, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='e', argrepr='e', has_arg=True, offset=15, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=1, argval='f', argrepr='f', has_arg=True, offset=18, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=6, argval=6, argrepr='6 positional, 0 keyword pair', has_arg=True, offset=21, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=24, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=0, argval=None, argrepr='None', has_arg=True, offset=25, starts_line=None, is_jump_target=False),
      Instruction(opname='RETURN_VALUE', opcode=83, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=28, starts_line=None, is_jump_target=False),
    ]

    expected_opinfo_jumpy = [
      Instruction(opname='SETUP_LOOP', opcode=120, optype='jrel', inst_size=3, arg=74, argval=77, argrepr='to 77', has_arg=True, offset=0, starts_line=3, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=0, argval='range', argrepr='range', has_arg=True, offset=3, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=1, argval=10, argrepr='10', has_arg=True, offset=6, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=9, starts_line=None, is_jump_target=False),
      Instruction(opname='GET_ITER', opcode=68, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=12, starts_line=None, is_jump_target=False),
      Instruction(opname='FOR_ITER', opcode=93, optype='jrel', inst_size=3, arg=50, argval=66, argrepr='to 66', has_arg=True, offset=13, starts_line=None, is_jump_target=True),
      Instruction(opname='STORE_FAST', opcode=125, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=16, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=19, starts_line=4, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=22, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=25, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=28, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=29, starts_line=5, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=2, argval=4, argrepr='4', has_arg=True, offset=32, starts_line=None, is_jump_target=False),
      Instruction(opname='COMPARE_OP', opcode=107, optype='compare', inst_size=3, arg=0, argval='<', argrepr='<', has_arg=True, offset=35, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=47, argval=47, argrepr='to 47', has_arg=True, offset=38, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=13, argval=13, argrepr='to 13', has_arg=True, offset=41, starts_line=6, is_jump_target=False),
      Instruction(opname='JUMP_FORWARD', opcode=110, optype='jrel', inst_size=3, arg=0, argval=47, argrepr='to 47', has_arg=True, offset=44, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=47, starts_line=7, is_jump_target=True),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=3, argval=6, argrepr='6', has_arg=True, offset=50, starts_line=None, is_jump_target=False),
      Instruction(opname='COMPARE_OP', opcode=107, optype='compare', inst_size=3, arg=4, argval='>', argrepr='>', has_arg=True, offset=53, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=13, argval=13, argrepr='to 13', has_arg=True, offset=56, starts_line=None, is_jump_target=False),
      Instruction(opname='BREAK_LOOP', opcode=80, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=59, starts_line=8, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=13, argval=13, argrepr='to 13', has_arg=True, offset=60, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=13, argval=13, argrepr='to 13', has_arg=True, offset=63, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_BLOCK', opcode=87, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=66, starts_line=None, is_jump_target=True),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=67, starts_line=10, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=4, argval='I can haz else clause?', argrepr="'I can haz else clause?'", has_arg=True, offset=70, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=73, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=76, starts_line=None, is_jump_target=False),
      Instruction(opname='SETUP_LOOP', opcode=120, optype='jrel', inst_size=3, arg=74, argval=154, argrepr='to 154', has_arg=True, offset=77, starts_line=11, is_jump_target=True),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=80, starts_line=None, is_jump_target=True),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=143, argval=143, argrepr='to 143', has_arg=True, offset=83, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=86, starts_line=12, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=89, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=92, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=95, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=96, starts_line=13, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=5, argval=1, argrepr='1', has_arg=True, offset=99, starts_line=None, is_jump_target=False),
      Instruction(opname='INPLACE_SUBTRACT', opcode=56, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=102, starts_line=None, is_jump_target=False),
      Instruction(opname='STORE_FAST', opcode=125, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=103, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=106, starts_line=14, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=3, argval=6, argrepr='6', has_arg=True, offset=109, starts_line=None, is_jump_target=False),
      Instruction(opname='COMPARE_OP', opcode=107, optype='compare', inst_size=3, arg=4, argval='>', argrepr='>', has_arg=True, offset=112, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=124, argval=124, argrepr='to 124', has_arg=True, offset=115, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=80, argval=80, argrepr='to 80', has_arg=True, offset=118, starts_line=15, is_jump_target=False),
      Instruction(opname='JUMP_FORWARD', opcode=110, optype='jrel', inst_size=3, arg=0, argval=124, argrepr='to 124', has_arg=True, offset=121, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=124, starts_line=16, is_jump_target=True),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=2, argval=4, argrepr='4', has_arg=True, offset=127, starts_line=None, is_jump_target=False),
      Instruction(opname='COMPARE_OP', opcode=107, optype='compare', inst_size=3, arg=0, argval='<', argrepr='<', has_arg=True, offset=130, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=80, argval=80, argrepr='to 80', has_arg=True, offset=133, starts_line=None, is_jump_target=False),
      Instruction(opname='BREAK_LOOP', opcode=80, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=136, starts_line=17, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=80, argval=80, argrepr='to 80', has_arg=True, offset=137, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_ABSOLUTE', opcode=113, optype='jabs', inst_size=3, arg=80, argval=80, argrepr='to 80', has_arg=True, offset=140, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_BLOCK', opcode=87, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=143, starts_line=None, is_jump_target=True),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=144, starts_line=19, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=6, argval='Who let lolcatz into this test suite?', argrepr="'Who let lolcatz into this test suite?'", has_arg=True, offset=147, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=150, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=153, starts_line=None, is_jump_target=False),
      Instruction(opname='SETUP_FINALLY', opcode=122, optype='jrel', inst_size=3, arg=72, argval=229, argrepr='to 229', has_arg=True, offset=154, starts_line=20, is_jump_target=True),
      Instruction(opname='SETUP_EXCEPT', opcode=121, optype='jrel', inst_size=3, arg=12, argval=172, argrepr='to 172', has_arg=True, offset=157, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=5, argval=1, argrepr='1', has_arg=True, offset=160, starts_line=21, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=7, argval=0, argrepr='0', has_arg=True, offset=163, starts_line=None, is_jump_target=False),
      Instruction(opname='BINARY_TRUE_DIVIDE', opcode=27, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=166, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=167, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_BLOCK', opcode=87, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=168, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_FORWARD', opcode=110, optype='jrel', inst_size=3, arg=28, argval=200, argrepr='to 200', has_arg=True, offset=169, starts_line=None, is_jump_target=False),
      Instruction(opname='DUP_TOP', opcode=4, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=172, starts_line=22, is_jump_target=True),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=2, argval='ZeroDivisionError', argrepr='ZeroDivisionError', has_arg=True, offset=173, starts_line=None, is_jump_target=False),
      Instruction(opname='COMPARE_OP', opcode=107, optype='compare', inst_size=3, arg=10, argval='exception match', argrepr='exception match', has_arg=True, offset=176, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_JUMP_IF_FALSE', opcode=114, optype='jabs', inst_size=3, arg=199, argval=199, argrepr='to 199', has_arg=True, offset=179, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=182, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=183, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=184, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=185, starts_line=23, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=8, argval='Here we go, here we go, here we go...', argrepr="'Here we go, here we go, here we go...'", has_arg=True, offset=188, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=191, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=194, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_EXCEPT', opcode=89, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=195, starts_line=None, is_jump_target=False),
      Instruction(opname='JUMP_FORWARD', opcode=110, optype='jrel', inst_size=3, arg=26, argval=225, argrepr='to 225', has_arg=True, offset=196, starts_line=None, is_jump_target=False),
      Instruction(opname='END_FINALLY', opcode=88, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=199, starts_line=None, is_jump_target=True),
      Instruction(opname='LOAD_FAST', opcode=124, optype='local', inst_size=3, arg=0, argval='i', argrepr='i', has_arg=True, offset=200, starts_line=25, is_jump_target=True),
      Instruction(opname='SETUP_WITH', opcode=143, optype='jrel', inst_size=3, arg=17, argval=223, argrepr='to 223', has_arg=True, offset=203, starts_line=None, is_jump_target=False),
      Instruction(opname='STORE_FAST', opcode=125, optype='local', inst_size=3, arg=1, argval='dodgy', argrepr='dodgy', has_arg=True, offset=206, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=209, starts_line=26, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=9, argval='Never reach this', argrepr="'Never reach this'", has_arg=True, offset=212, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=215, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=218, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_BLOCK', opcode=87, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=219, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=0, argval=None, argrepr='None', has_arg=True, offset=220, starts_line=None, is_jump_target=False),
      Instruction(opname='WITH_CLEANUP', opcode=81, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=223, starts_line=None, is_jump_target=True),
      Instruction(opname='END_FINALLY', opcode=88, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=224, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_BLOCK', opcode=87, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=225, starts_line=None, is_jump_target=True),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=0, argval=None, argrepr='None', has_arg=True, offset=226, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_GLOBAL', opcode=116, optype='name', inst_size=3, arg=1, argval='print', argrepr='print', has_arg=True, offset=229, starts_line=28, is_jump_target=True),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=10, argval="OK, now we're done", argrepr='"OK, now we\'re done"', has_arg=True, offset=232, starts_line=None, is_jump_target=False),
      Instruction(opname='CALL_FUNCTION', opcode=131, optype='nargs', inst_size=3, arg=1, argval=1, argrepr='1 positional, 0 keyword pair', has_arg=True, offset=235, starts_line=None, is_jump_target=False),
      Instruction(opname='POP_TOP', opcode=1, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=238, starts_line=None, is_jump_target=False),
      Instruction(opname='END_FINALLY', opcode=88, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=239, starts_line=None, is_jump_target=False),
      Instruction(opname='LOAD_CONST', opcode=100, optype='const', inst_size=3, arg=0, argval=None, argrepr='None', has_arg=True, offset=240, starts_line=None, is_jump_target=False),
      Instruction(opname='RETURN_VALUE', opcode=83, optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=243, starts_line=None, is_jump_target=False),
    ]


    # One last piece of inspect fodder to check the default line number handling
    def simple(): pass
    expected_opinfo_simple = [
      Instruction(opname='LOAD_CONST',   opcode=100, optype='const', inst_size= 3, arg=0,    argval=None, argrepr='None', has_arg=True, offset=0, starts_line=simple.__code__.co_firstlineno, is_jump_target=False),
      Instruction(opname='RETURN_VALUE', opcode=83,  optype=None, inst_size=1, arg=None, argval=None, argrepr='', has_arg=False, offset=3, starts_line=None, is_jump_target=False)
    ]


    class InstructionTests(BytecodeTestCase):

        def test_default_first_line(self):
            actual = dis.get_instructions(simple)
            self.assertEqual(list(actual), expected_opinfo_simple)

        def test_first_line_set_to_None(self):
            actual = dis.get_instructions(simple, first_line=None)
            self.assertEqual(list(actual), expected_opinfo_simple)

        def test_outer(self):
            actual = dis.get_instructions(outer, first_line=expected_outer_line)
            self.assertEqual(list(actual), expected_opinfo_outer)

        def test_nested(self):
            with captured_stdout():
                f = outer()
            actual = dis.get_instructions(f, first_line=expected_f_line)
            self.assertEqual(list(actual), expected_opinfo_f)

        def test_doubly_nested(self):
            with captured_stdout():
                inner = outer()()
            actual = dis.get_instructions(inner, first_line=expected_inner_line)
            self.assertEqual(list(actual), expected_opinfo_inner)

        # def test_jumpy(self):
        #     actual = dis.get_instructions(jumpy, first_line=expected_jumpy_line)
        #     self.assertEqual(list(actual), expected_opinfo_jumpy)

    # get_instructions has its own tests above, so can rely on it to validate
    # the object oriented API
    class BytecodeTests(unittest.TestCase):
        def test_instantiation(self):
            # Test with function, method, code string and code object
            for obj in [_f, _C(1).__init__, "a=1", _f.__code__]:
                with self.subTest(obj=obj):
                    b = dis.Bytecode(obj)
                    self.assertIsInstance(b.codeobj, types.CodeType)

            self.assertRaises(TypeError, dis.Bytecode, object())

        def test_iteration(self):
            for obj in [_f, _C(1).__init__, "a=1", _f.__code__]:
                with self.subTest(obj=obj):
                    via_object = list(dis.Bytecode(obj))
                    via_generator = list(dis.get_instructions(obj))
                    self.assertEqual(via_object, via_generator)

        def test_explicit_first_line(self):
            actual = dis.Bytecode(outer, first_line=expected_outer_line)
            self.assertEqual(list(actual), expected_opinfo_outer)

        def test_source_line_in_disassembly(self):
            # Use the line in the source code
            actual = dis.Bytecode(simple).dis()[:3]
            expected = "{:>3}".format(simple.__code__.co_firstlineno)
            self.assertEqual(actual, expected)
            # Use an explicit first line number
            actual = dis.Bytecode(simple, first_line=350).dis()[:3]
            self.assertEqual(actual, "350")

        def test_info(self):
            self.maxDiff = 1000
            for x, expected in CodeInfoTests.test_pairs:
                b = dis.Bytecode(x)
                self.assertRegex(b.info(), expected)

        def test_disassembled(self):
            actual = dis.Bytecode(_f).dis()
            self.skipTest('fix test_disassembled')
            self.assertEqual(actual, dis_f)

        def test_from_traceback(self):
            tb = get_tb()
            b = dis.Bytecode.from_traceback(tb)
            while tb.tb_next: tb = tb.tb_next

            self.assertEqual(b.current_offset, tb.tb_lasti)

        def test_from_traceback_dis(self):
            tb = get_tb()
            b = dis.Bytecode.from_traceback(tb)
            self.skipTest('fix test_from_traceback_dis')
            self.assertEqual(b.dis(), dis_traceback)

if __name__ == "__main__":
    unittest.main()
