"""xdis.bytecode testing"""

# Below, we first give some test code to work on.

# This code is sensitive to the line number ordering.
# By adding test code at the top we reduce line-number
# ordering sensistivity.

# From 2.7 disassemble
# Problem is that "while" loop
# has two linestarts in it and
# they are in co_lnotab.
# Sometimes we need to lie and say
# there is only one offset there.

def bug_loop(disassemble, tb=None):
    if tb:
        try:
            tb = 5
        except AttributeError:
            raise RuntimeError
        while tb: tb = tb.tb_next
    disassemble(tb)

import sys
from xdis import PYTHON_VERSION, findlinestarts
from xdis.opcodes import opcode_27, opcode_36
from xdis.load import load_module
from xdis.bytecode import offset2line

import os.path as osp

def test_offset2line():
    ary = ((20, 1), (40, 10), (60, 45))
    for offset, expect in (
            (61, 45),
            (20, 1),
            (40, 10),
            (39, 1),
            (41, 10),
            (60, 45),
            (21, 1)):
        got = offset2line(offset, ary)
        assert expect == got, \
            ("offset=%d, got=%d, expect=%d" % (offset, got, expect))
    ary = ((20, 1), (50, 10))
    for offset, expect in (
            (10, 0),
            (55, 10),
            (20, 1),
            (50, 10)):
        got = offset2line(offset, ary)
        assert expect == got, \
            ("offset=%d, got=%d, expect=%d" % (offset, got, expect))
    ary = ((25, 1),)
    for offset, expect in (
            (10, 0),
            (30, 1),
            (25, 1)):
        got = offset2line(offset, ary)
        assert expect == got, \
            ("offset=%d, got=%d, expect=%d" % (offset, got, expect))
    ary = tuple()
    for offset, expect in ((10, 0),):
        got = offset2line(offset, ary)
        assert expect == got, \
            ("offset=%d, got=%d, expect=%d" % (offset, got, expect))

def test_find_linestarts():
    co= bug_loop.__code__
    # start_line = co.co_firstlineno
    got_no_dups = list(findlinestarts(co))

    if sys.version_info[0:2] == (2,7):
        # FIXME base off of start_line
        expect = [(0, 17), (6, 18), (9, 19), (19, 20), (32, 21), (42, 22),
                  (67, 23)]
        assert got_no_dups == expect

    got_with_dups = list(findlinestarts(bug_loop.__code__, dup_lines=True))
    if sys.version_info[0:2] >= (3,9):
        assert len(got_no_dups) <= len(got_with_dups)
    else:
        assert len(got_no_dups) < len(got_with_dups)

# FIXME: a feature of doing code this way is that
# this compiles to the running version of code
def bug708901():
    for res in range(1,
                     10):
        pass

def findlabels():
    my_dir = osp.dirname(osp.abspath(__file__))

    # Python 2.7 code
    code = bug708901.__code__

    # FIXME: Consider loading from a file like below to remove
    # dependence on running interpreter
    if PYTHON_VERSION == 2.7:
        # 19:           0 SETUP_LOOP               23 (to 26)
        #               3 LOAD_GLOBAL               0 (range)
        #               6 LOAD_CONST                1 (1)
        #
        # 20:           9 LOAD_CONST                2 (10)
        #              12 CALL_FUNCTION             2 (2 positional, 0 keyword pair)
        #              15 GET_ITER
        #         >>   16 FOR_ITER                  6 (to 25)
        #              19 STORE_FAST                0 (res)
        #
        # 21:          22 JUMP_ABSOLUTE            16 (to 16)
        #         >>   25 POP_BLOCK
        #         >>   26 LOAD_CONST                0 (None)
        #              29 RETURN_VALUE
        offset_map = opcode_27.get_jump_target_maps(code,  opcode_27)

        expected = { 3: [0], 6: [3], 9: [6], 12: [9], 15: [12],
                    16: [15, 22], 19: [16], 22: [19], 25: [16],
                    26: [0, 25], 29: [26]}
        assert expected == offset_map

        offsets = opcode_27.get_jump_targets(code,  opcode_27)
        assert offsets == [26, 25, 16]

    test_pyc = my_dir +'/../test/bytecode_2.7/01_dead_code.pyc'
    (version, timestamp, magic_int, co, pypy,
     source_size, _) = load_module(test_pyc)
    code = co.co_consts[0]
    offsets = opcode_27.get_jump_targets(code,  opcode_27)
    assert [10] == offsets

    # from xdis import disassemble_file
    # print('\n')
    # disassemble_file(test_pyc)

    #  2:           0 LOAD_FAST                 0 (a)
    #               3 POP_JUMP_IF_FALSE        10 (to 10)
    #
    #  3:           6 LOAD_CONST                1 (5)
    #               9 RETURN_VALUE
    #
    #  5:     >>   10 LOAD_CONST                2 (6)
    #              13 RETURN_VALUE
    #              14 LOAD_CONST                0 (None)
    #              17 RETURN_VALUE
    offset_map = opcode_27.get_jump_target_maps(code,  opcode_27)
    # print(offset_map)
    expect = {3: [0], 6: [3], 9: [6], 10: [3], 13: [10], 17: [14]}
    assert expect == offset_map

    # Python 3.6 code wordcode
    # ------------------------
    test_pyc = my_dir +'/../test/bytecode_3.6/01_dead_code.pyc'
    (version, timestamp, magic_int, co, pypy,
     source_size, _) = load_module(test_pyc)
    code = co.co_consts[0]

    #  2:           0 LOAD_FAST                 0 (a)
    #               2 POP_JUMP_IF_FALSE         8 (to 8)
    #
    #  3:           4 LOAD_CONST                1 (5)
    #               6 RETURN_VALUE
    #
    #  5:           8 LOAD_CONST                2 (6)
    #              10 RETURN_VALUE
    #              12 LOAD_CONST                0 (None)
    #              14 RETURN_VALUE

    offsets = opcode_36.get_jump_targets(code,  opcode_36)
    assert offsets == [8]

    from xdis import disassemble_file
    print('\n')
    disassemble_file(test_pyc)

    offset_map = opcode_36.get_jump_target_maps(code,  opcode_36)
    expect = {2: [0], 4: [2], 6: [4], 8: [2], 10: [8], 14: [12]}
    assert expect == offset_map

if __name__ == "__main__":
    # test_get_jump_targets()
    # test_offset2line()
    test_find_linestarts()
