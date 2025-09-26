"""
Unit test for xdis.magics
"""
import pytest
from xdis.magics import MAGIC, sysinfo2magic
from xdis.version_info import PYTHON_VERSION_TRIPLE


@pytest.mark.skipif(
    PYTHON_VERSION_TRIPLE >= (3, 14),
    reason="Python >= 3.14 is not complete.",
)
def test_magic():
    assert sysinfo2magic() == MAGIC, (sysinfo2magic(), MAGIC)
