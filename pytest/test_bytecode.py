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

from xdis.bytecode import offset2line
from xdis.opcodes.opcode_27 import findlinestarts
import sys

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
