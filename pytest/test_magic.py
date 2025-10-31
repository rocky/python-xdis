"""
Unit test for xdis.magics
"""

import pytest
from xdis.magics import (
    INTERIM_MAGIC_INTS,
    MAGIC,
    magicint2version,
    minor_release_names,
    sysinfo2magic,
    version2magicint,
)
from xdis.version_info import PYTHON_VERSION_TRIPLE


@pytest.mark.skipif(
    PYTHON_VERSION_TRIPLE >= (3, 14),
    reason="Python >= 3.14 is not complete.",
)
def test_magic():
    assert sysinfo2magic() == MAGIC, (sysinfo2magic(), MAGIC)

    # Check that our interim version numbers are not used as release numbers.
    interim_version_names = {
        magicint2version[magic_int] for magic_int in INTERIM_MAGIC_INTS
    }
    incorrect_interim_names = interim_version_names.intersection(minor_release_names)
    if interim_version_names:
        for incorrect_name in incorrect_interim_names:
            print("Remove %s %s" % (incorrect_name, version2magicint[incorrect_name]))
    assert (
        not incorrect_interim_names
    ), "Remove magic numbers for %s" % incorrect_interim_names
