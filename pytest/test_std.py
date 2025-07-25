# std
import os
import shutil
import sys
import tempfile
from contextlib import closing
from datetime import datetime

# compat
import six

# 3rd party
import pytest

# local
import xdis.std as dis
from xdis import (
    IS_GRAAL,
    IS_PYPY,
    PYTHON3,
    PYTHON_VERSION_TRIPLE,
    Code3,
    list2bytecode,
    opcodes,
    write_bytecode_file,
)

if PYTHON_VERSION_TRIPLE >= (3, 2):
    if pytest.__version__ >= "3.2.0":
        yield_fixture = pytest.fixture
    else:
        yield_fixture = pytest.yield_fixture


# just a simple bit of code that should be the same across python versions,
# we are testing the api here really, leave it to the other tests to perform
# more complicated implementation verification.


TEST_SOURCE_CODE = "a = 10"
TEST_CODE = compile(TEST_SOURCE_CODE, "<disassembly>", "single")


TEST_BRANCH_SOURCE_CODE = "a = 0 if 1 else 2"
TEST_BRANCH_CODE = compile(TEST_BRANCH_SOURCE_CODE, "<disassembly>", "single")


EXPECTED_CODE_INFO = (
    """# Method Name:       <module>
# Filename:          <disassembly>
# Argument count:    0
"""
    + ("# Position-only argument count: 0\n" if PYTHON_VERSION_TRIPLE >= (3, 8) else "")
    + ("# Keyword-only arguments: 0\n" if PYTHON3 else "")
    + """# Number of locals:  0
# Stack size:        1
# Flags:             {flags}
# First Line:        1
# Constants:
#    0: 10
#    1: None
# Names:
#    0: a"""
).format(
    flags="0x00000000 (0x0)"
    if (PYTHON_VERSION_TRIPLE >= (3, 11) and not IS_PYPY) or (IS_PYPY and PYTHON_VERSION_TRIPLE < (3, 5))
    else "0x00000040 (NOFREE)"
)

EXPECTED_DIS = """\
  1:           0 LOAD_CONST           (10)
               3 STORE_NAME           (a)
               6 LOAD_CONST           (None)
               9 RETURN_VALUE
"""

EXPECTED_DIS_36 = """\
  1:           0 LOAD_CONST           (10)
               2 STORE_NAME           (a)
               4 LOAD_CONST           (None)
               6 RETURN_VALUE
"""

if PYTHON_VERSION_TRIPLE < (3, 6):
    expected_dis = EXPECTED_DIS
else:
    expected_dis = EXPECTED_DIS_36


if PYTHON_VERSION_TRIPLE >= (3, 2) and not IS_GRAAL:

    @pytest.fixture
    def bytecode_fixture():
        return dis.Bytecode(TEST_SOURCE_CODE)

    @pytest.fixture
    def traceback_fixture():
        try:
            raise Exception
        except Exception:
            _, _, tb = sys.exc_info()
            return tb

    @yield_fixture
    def stream_fixture():
        with closing(six.StringIO()) as s:
            yield s

    def test_bytecode_from_traceback(traceback_fixture):
        assert len(list(dis.Bytecode.from_traceback(traceback_fixture))) > 0

    def test_bytecode_codeobj(bytecode_fixture):
        assert bytecode_fixture.codeobj is not None

    def test_bytecode_first_line(bytecode_fixture):
        assert bytecode_fixture.first_line is not None

    # def test_bytecode_dis(bytecode_fixture):
    #     assert bytecode_fixture.dis() == expected_dis

    def test_bytecode_info(bytecode_fixture):
        actual = bytecode_fixture.info()
        assert actual == EXPECTED_CODE_INFO

    def test_bytecode__iter__(bytecode_fixture):
        assert len(list(bytecode_fixture)) > 0

    def test_code_info():
        assert dis.code_info(TEST_SOURCE_CODE) == EXPECTED_CODE_INFO

    def test_show_code(stream_fixture):
        dis.show_code(TEST_SOURCE_CODE, file=stream_fixture)
        actual = stream_fixture.getvalue()
        assert actual == EXPECTED_CODE_INFO + "\n"

    def test_pretty_flags():
        assert dis.pretty_flags(1) == "0x00000001 (OPTIMIZED)"

    # def test_dis(stream_fixture):
    #     dis.dis(TEST_SOURCE_CODE, file=stream_fixture)
    #     actual = stream_fixture.getvalue()
    #     assert actual == expected_dis + '\n'

    def test_distb(traceback_fixture, stream_fixture):
        dis.distb(traceback_fixture, file=stream_fixture)
        actual = stream_fixture.getvalue()
        actual_len = len(actual)
        assert actual_len > 0

    # def test_disassemble(stream_fixture):
    #     dis.disassemble(TEST_CODE, file=stream_fixture)
    #     actual = stream_fixture.getvalue()[8:]
    #     expected = EXPECTED_CODE_INFO + '\n' + expected_dis + '\n'
    #     print("\n".split(expected)expected)
    #     assert actual == expected

    def test_get_instructions():
        actual = list(dis.get_instructions(TEST_SOURCE_CODE))
        actual_len = len(actual)
        assert actual_len > 0

    @pytest.mark.skipif(
        IS_PYPY, reason="Pypy can't be converted to a floating point number"
    )
    def test_make_std_api():
        api24_tup = dis.make_std_api((2, 4, 6, "final", 0))
        api24_float = dis.make_std_api(2.4)
        assert (
            api24_tup.opmap == api24_float.opmap
        ), "Can get std_api using a floating-point number"

    def test_findlinestarts():
        actual = list(dis.findlinestarts(TEST_CODE))
        actual_len = len(actual)
        assert actual_len > 0

    @pytest.mark.skipif(
        PYTHON_VERSION_TRIPLE >= (3, 10),
        reason="Python 3.10 and above doesn't have branches in this code",
    )
    def test_findlabels():
        if PYTHON_VERSION_TRIPLE < (3, 6):
            test_code = TEST_BRANCH_CODE
        else:
            test_code = TEST_BRANCH_CODE.co_code

        actual = list(dis.findlabels(test_code))
        actual_len = len(actual)
        assert actual_len > 0

    def _create_python3_code_object():
        consts = (None, 2)
        varnames = ("a",)
        instructions = [
            ("LOAD_CONST", 2),
            ("STORE_FAST", "a"),
            ("LOAD_FAST", "a"),
            ("RETURN_VALUE",),
        ]

        text = "def fact():\n\ta = 8\n\ta = 0\n"

        code = list2bytecode(instructions, opcodes.opcode_34, varnames, consts)
        fn_code = compile(text, "<string>", "exec")
        return Code3(
            fn_code.co_argcount,
            fn_code.co_kwonlyargcount,  # Add this in Python3
            fn_code.co_nlocals,
            fn_code.co_stacksize,
            fn_code.co_flags,
            # These are changed
            code,
            consts,
            fn_code.co_names,
            varnames,
            fn_code.co_filename,
            fn_code.co_name,
            fn_code.co_firstlineno,
            fn_code.co_lnotab,  # In general, You should adjust this
            fn_code.co_freevars,
            fn_code.co_cellvars,
        )

    def test_write_bytecode_file():
        temp_dir = tempfile.mkdtemp()
        target_path = os.path.join(temp_dir, "test1.pyc")
        code_object = _create_python3_code_object()
        write_bytecode_file(target_path, code_object, 3394, 10)
        shutil.rmtree(temp_dir)

    def test_write_bytecode_bad_timestamp_type():
        temp_dir = tempfile.mkdtemp()
        target_path = os.path.join(temp_dir, "test2.pyc")
        code_object = _create_python3_code_object()
        with pytest.raises(TypeError):
            write_bytecode_file(
                target_path, code_object, 3394, datetime.now().timestamp()
            )
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_findlabels()
    # test_find_linestarts()
