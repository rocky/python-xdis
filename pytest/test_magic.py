"""
Unit test for xdis.magics
"""
from xdis import IS_GRAAL
from xdis.magics import MAGIC, sysinfo2magic


def test_magic():
    assert sysinfo2magic() == MAGIC, (sysinfo2magic(), MAGIC)
