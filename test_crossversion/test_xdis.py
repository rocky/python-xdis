from __future__ import annotations

from itertools import chain

from pathlib import Path
from typing import Iterable

import pytest
from config import SYS_VERSION, TEMPLATE_COMPILED_DIR, TEMPLATE_SERIALIZED_DIR
from serialize_bytecode import serialize_pyc


class SerializedTestCase:
    """Test case for comparing a disassembled xdis and dis pyc, Needs a pyc to
    disassemble with xdis then serialize, and a dis serialized pyc txt file."""

    pyc_path: Path
    serialized_txt_path: Path
    serialized_dis: str
    serialized_xdis: str
    message: str

    def __init__(self, pyc: Path, serialized_txt: Path):
        self.pyc_path = pyc
        self.serialized_txt_path = serialized_txt
        self.serialized_dis = serialized_txt.read_text()
        self.serialized_xdis = serialize_pyc(pyc, use_xdis=True, output_file=None)
        self.message = (
            f"Checking equivalence: {self.pyc_path} <---> {self.serialized_txt_path}"
        )

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return self.__str__()


def get_versions() -> Iterable[str]:
    """Get test versions by iterating through dirs in template compiled dir."""
    for dir in TEMPLATE_COMPILED_DIR.glob("*"):
        if dir.is_dir():
            yield dir.name


def get_tests_by_version(v: str) -> Iterable[SerializedTestCase]:
    """Iterate test cases from Template folder with given version v."""
    compiled_tests_dir = Path(TEMPLATE_COMPILED_DIR / v)
    serialized_tests_dir = Path(TEMPLATE_SERIALIZED_DIR / v)
    assert compiled_tests_dir.exists()
    assert serialized_tests_dir.exists()

    for compiled_test in compiled_tests_dir.glob("*"):
        test_stem = compiled_test.stem
        serialized_test = Path(serialized_tests_dir / (test_stem + ".txt"))

        # check test case pair
        assert serialized_test.exists() and compiled_test.exists()
        yield SerializedTestCase(compiled_test, serialized_test)


# @pytest.mark.parametrize("version", get_versions())
# def test_version(version):
#     """Test each version in compiled template folder."""
#     for case in get_tests_by_version(version):
#         assert case.serialized_dis.splitlines() == case.serialized_xdis.splitlines()


@pytest.mark.parametrize(
    "case", chain.from_iterable(get_tests_by_version(v) for v in get_versions())
)
def test_case(case: SerializedTestCase):
    assert case.serialized_dis.splitlines() == case.serialized_xdis.splitlines()
