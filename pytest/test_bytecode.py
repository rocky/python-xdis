from xdis.bytecode import offset2line

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
