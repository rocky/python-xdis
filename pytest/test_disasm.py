import os.path
import pytest
import re

from xdis.main import disassemble_file
from xdis import PYTHON3

if PYTHON3:
    from io import StringIO
else:
    from StringIO import StringIO

def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)

src_dir = get_srcdir()
os.chdir(src_dir)


@pytest.mark.parametrize(("test_tuple", "function_to_test"), [
    (
        ('../test/bytecode_3.6/01_fstring.pyc', 'testdata/fstring-3.6.right',),
        disassemble_file,
    ),
    (
        ('../test/bytecode_3.0/04_raise.pyc', 'testdata/raise-3.0.right',),
        disassemble_file,
    ),
    (
        ('../test/bytecode_pypy2.7/04_pypy_lambda.pyc', 'testdata/pypy_lambda.right',),
        disassemble_file,
    ),
])

def test_funcoutput(capfd, test_tuple, function_to_test):
    in_file, filename_expected = test_tuple
    resout = StringIO()
    function_to_test(in_file, resout)
    expected = "".join(open(filename_expected, "r").readlines())
    got_lines = resout.getvalue().split("\n")
    got_lines = [re.sub(' at 0x[0-9a-f]+, file', ' at 0xdeadbeef0000, file', line)
                 for line in got_lines]
    got = "\n".join(got_lines[5:])

    if got != expected:
        with open(filename_expected + ".got", "w") as out:
            out.write(got)
    assert got == expected
