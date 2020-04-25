import os, sys
from xdis import IS_PYPY, PYTHON_VERSION
from xdis.load import load_file, check_object_path, load_module
from xdis.codetype import CodeTypeUnionFields

import os.path as osp


def get_srcdir():
    filename = osp.normcase(os.path.dirname(os.path.abspath(__file__)))
    return osp.realpath(filename)

def test_load_file():
    srcdir = get_srcdir()
    setup_file = osp.realpath(osp.join(srcdir, "..", "xdis", "load.py"))

    co_file = load_file(setup_file)
    obj_path = check_object_path(setup_file)
    (version, timestamp, magic_int, co_module, pypy,
     source_size, sip_hash) = load_module(obj_path)
    if 3.3 <= version <= 3.7:
        statinfo = os.stat(__file__)
        # FIXME: why does this fail?
        # assert statinfo.st_size == source_size
        assert sip_hash is None
    elif version < 3.3:
        assert source_size is None, source_size
        assert sip_hash is None

    for field in CodeTypeUnionFields:
        if hasattr(co_file, field):
            load_file_field = getattr(co_file, field)
            load_module_field = getattr(co_module, field)
            assert load_module_field == load_file_field, (
                "field %s\nmodule:\n\t%s\nfile:\n\t%s" % (field, load_module_field, load_file_field)
                )
            print("ok %s" % field)

if __name__ == '__main__':
    test_load_file()
