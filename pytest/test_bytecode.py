"""xdis.bytecode testing"""

# Some test code first since we wan to reduce
# the amount of line number jiggling if this
# teste changes.

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
from xdis.opcodes import opcode_27, opcode_36
from xdis.load import load_module
from xdis.bytecode import offset2line
from xdis.opcodes.opcode_27 import findlinestarts

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
        expect = [(0, 15), (6, 16), (9, 17), (19, 18), (32, 19), (42, 20),
                  (67, 21)]
        assert got_no_dups == expect

    got_with_dups = list(findlinestarts(bug_loop.__code__, dup_lines=True))
    assert len(got_no_dups) < len(got_with_dups)

def test_get_jump_targets():
    my_dir = osp.dirname(osp.abspath(__file__))

    # Python 2.7 code
    test_pyc = my_dir +'/../test/bytecode_2.7/01_dead_code.pyc'
    (version, timestamp, magic_int, co, pypy,
     source_size) = load_module(test_pyc)
    dead_code_co = co.co_consts[0]
    offsets = opcode_27.get_jump_targets(dead_code_co,  opcode_27)
    assert [10] == offsets

    # import xdis.std as dis
    # print('\n')
    # dis.dis(dead_code_co)

    offset_map = opcode_27.get_jump_target_maps(dead_code_co,  opcode_27)
    # print(offset_map)
    expect = {3: [0], 6: [3], 9: [6], 10: [6], 13: [10], 17: [14]}
    assert expect == offset_map

    # Python 3.6 code wordcode
    test_pyc = my_dir +'/../test/bytecode_3.6/01_dead_code.pyc'
    (version, timestamp, magic_int, co, pypy,
     source_size) = load_module(test_pyc)
    dead_code_co = co.co_consts[0]
    offsets = opcode_36.get_jump_targets(dead_code_co,  opcode_36)
    assert offsets == [8]

    # from xdis.main import disassemble_file
    # print('\n')
    # disassemble_file(test_pyc)

    offset_map = opcode_36.get_jump_target_maps(dead_code_co,  opcode_36)
    expect = {2: [0], 4: [2], 6: [4], 8: [2], 10: [8], 14: [12]}
    assert expect == offset_map
