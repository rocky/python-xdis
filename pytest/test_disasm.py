import os
import platform
import re
from io import StringIO
from typing import List

import pytest
from xdis import disassemble_file
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE

hextring_file = "testdata/01_hexstring-2.7-for3x.right"


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(__file__))
    return os.path.realpath(filename)


def disassemble_file_extended_bytes(file, resout):
    disassemble_file(file, resout, asm_format="extended-bytes")


def disassemble_file_xasm(file, resout):
    disassemble_file(file, resout, asm_format="xasm")


def run_check_disasm(test_tuple, function_to_test):
    in_file, filename_expected = [os.path.join(get_srcdir(), p) for p in test_tuple]
    resout = StringIO()
    function_to_test(in_file, resout)
    expected_lines = open(filename_expected, "r").readlines()
    expected = "".join(expected_lines)
    got_lines = resout.getvalue().split("\n")
    if platform.python_implementation() in ("GraalVM", "PyPy"):
        got_lines = got_lines[1:]
    got_lines = [
        re.sub(" at 0x[0-9a-f]+", " at 0xdeadbeef0000", line) for line in got_lines
    ]
    got_lines = [
        re.sub(
            "<code object .+, line|<Code.+ code object .+, line",
            "<code object at 0xdeadbeef0001, line",
            line,
        )
        for line in got_lines
    ]
    got_lines = [
        re.sub(
            "# Method Name:       lambda_0x[0-9a-f]+",
            "# Method Name:       lambda_0xdeadbeef0002",
            line,
        )
        for line in got_lines
    ]

    # In Python before 3.10 lines describing Python versions were
    # two lines, e.g.:
    #  Python 3.7.11 (default, Jul  3 2021, 19:46:46)
    #    [GCC 9.3.0]
    # In Python 3.10 they are a single line, e.g:
    #    Python 3.10.0 (default, Oct  4 2021, 23:36:04) [GCC 9.3.0]
    skip_lines = 4 if PYTHON_VERSION_TRIPLE >= (3, 10) else 5
    if IS_PYPY:
        if (3, 5) <= PYTHON_VERSION_TRIPLE[:2] <= (3, 9):
            # PyPy also adds a timestamp line
            skip_lines -= 1

    got = "\n".join(got_lines[skip_lines:])

    if "XDIS_DONT_WRITE_DOT_GOT_FILES" not in os.environ:
        if got != expected:
            got_filename = filename_expected + ".got"
            with open(got_filename, "w") as out:
                out.write(got)
        assert got == expected, f"see {got_filename} for diffs"
    else:
        assert got == expected


# FIXME: redo
# (
#     ("../test/bytecode_3.0/04_raise.pyc", "testdata/raise-3.0.right"),
#     disassemble_file,
# ),
# (
#  ("../test/bytecode_2.7/01_hexstring.pyc", hextring_file),
#   disassemble_file,
#  ),


# FIXME: redo putting more in loop. Add more Python versions and
# more formats
@pytest.mark.skipif(
    os.name == "nt", reason="Windows differences in output need going over"
)
@pytest.mark.parametrize(
    ("test_name", "version", "formats"),
    [
        ("01_fstring", "3.6", ["classic", "xasm"]),
        # ("01_fstring", "3.10"),  # FIXME
        ("04_pypy_lambda", "2.7pypy", ["classic", "xasm"]),
        ("03_big_dict", "2.7", ["classic", "xasm"]),
        ("03_big_dict", "3.3", ["classic", "xasm"]),
        ("03_big_dict", "3.5", ["classic", "xasm"]),
        ("03_big_dict", "3.6", ["classic", "xasm"]),
        ("03_big_dict", "3.6", ["classic", "xasm"]),
        ("03_annotations", "3.7", ["classic", "xasm"]),
        ("test_nested_scopes", "2.1", ["extended-bytes"]),
        # ("01_augmented_assign", "3.7", ["extended-bytes"]),
        # ("03_big_dict", "3.10"), # FIXME
    ],
)
def test_funcoutput(test_name, version, formats: List[str]):
    if "classic" in formats:
        test_tuple = (
            f"../test/bytecode_{version}/{test_name}.pyc",
            f"testdata/{test_name}-{version}.right",
        )
        run_check_disasm(test_tuple, disassemble_file)
    if "extended-bytes" in formats:
        test_tuple = (
            f"../test/bytecode_{version}/{test_name}.pyc",
            f"testdata/{test_name}-extended-bytes-{version}.right",
        )
        run_check_disasm(test_tuple, disassemble_file_extended_bytes)
    if "xasm" in formats:
        test_tuple = (
            f"../test/bytecode_{version}/{test_name}.pyc",
            f"testdata/{test_name}-xasm-{version}.right",
        )
        run_check_disasm(test_tuple, disassemble_file_xasm)


if __name__ == "__main__":
    test_funcoutput(
        ("../test/bytecode_3.0/04_raise.pyc", "testdata/raise-3.0.right"),
        disassemble_file,
        ["classic"],
    )
