import os, pytest, sys
from xdis import IS_PYPY
from xdis.load import load_file, check_object_path, load_module

@pytest.mark.skipif(sys.version_info >= (3,5),
                    reason="Doesn't work on 3.5 and later")
def test_load_file():
    co = load_file(__file__)
    obj_path = check_object_path(__file__)
    (version, timestamp, magic_int, co2, pypy,
     source_size) = load_module(obj_path)
    if (3,0) <= sys.version_info:
        statinfo = os.stat(__file__)
        assert statinfo.st_size == source_size
    else:
        assert source_size is None

    if IS_PYPY:
        assert str(co) == str(co2)
    else:
        assert co == co2
