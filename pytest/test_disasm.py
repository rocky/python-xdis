import os
import pytest
import re

from xdis import disassemble_file
from xdis.version_info import PYTHON3, PYTHON_VERSION_TRIPLE

if PYTHON3:
    from io import StringIO

    hextring_file = "testdata/01_hexstring-2.7-for3x.right"
else:
    from StringIO import StringIO

    hextring_file = "testdata/01_hexstring-2.7.right"


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)


if PYTHON_VERSION_TRIPLE >= (3, 2):
    @pytest.mark.parametrize(
        ("test_tuple", "function_to_test"),
        [
            (
                ("../test/bytecode_3.6/01_fstring.pyc", "testdata/fstring-3.6.right"),
                disassemble_file,
            ),
            (
                ("../test/bytecode_3.0/04_raise.pyc", "testdata/raise-3.0.right"),
                disassemble_file,
            ),
            (
                (
                    "../test/bytecode_2.7pypy/04_pypy_lambda.pyc",
                    "testdata/pypy_lambda.right",
                ),
                disassemble_file,
            ),
            (
                ("../test/bytecode_3.6/03_big_dict.pyc", "testdata/big_dict-3.6.right"),
                disassemble_file,
            ),
            (("../test/bytecode_2.7/01_hexstring.pyc", hextring_file), disassemble_file),
        ],
    )
    def test_funcoutput(capfd, test_tuple, function_to_test):
        in_file, filename_expected = [os.path.join(get_srcdir(), p) for p in test_tuple]
        resout = StringIO()
        function_to_test(in_file, resout)
        expected = "".join(open(filename_expected, "r").readlines())
        got_lines = resout.getvalue().split("\n")
        got_lines = [
            re.sub(" at 0x[0-9a-f]+", " at 0xdeadbeef0000", line) for line in got_lines
        ]
        got_lines = [
            re.sub(
                "<code object .*>|<Code.+ code object .*>",
                "<code object at 0xdeadbeef0000>",
                line,
            )
            for line in got_lines
        ]

        # In Python before 3.10 lines decribing Python versions were
        # two lines, e.g.:
        #  Python 3.7.11 (default, Jul  3 2021, 19:46:46)
        #    [GCC 9.3.0]
        # In Python 3.10 they are a single line, e.g:
        #    Python 3.10.0 (default, Oct  4 2021, 23:36:04) [GCC 9.3.0]
        skip_lines = 4 if PYTHON_VERSION_TRIPLE >= (3, 10) else 5
        got = "\n".join(got_lines[skip_lines:])

        if "XDIS_DONT_WRITE_DOT_GOT_FILES" not in os.environ:
            if got != expected:
                with open(filename_expected + ".got", "w") as out:
                    out.write(got)
        assert got == expected

if __name__ == "__main__":
    import sys
    test_funcoutput(sys.stdout, ("../test/bytecode_3.0/04_raise.pyc", "testdata/raise-3.0.right"),
                    disassemble_file)
