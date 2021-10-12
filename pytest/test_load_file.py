import os
from xdis import IS_PYPY
from xdis.load import load_file, check_object_path, load_module
from xdis.codetype import CodeTypeUnionFields

import os.path as osp


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def test_load_file():
    srcdir = get_srcdir()
    load_py = osp.realpath(osp.join(srcdir, "..", "xdis", "load.py"))

    co_file = load_file(load_py)
    obj_path = check_object_path(load_py)
    (
        version_tuple,
        timestamp,
        magic_int,
        co_module,
        pypy,
        source_size,
        sip_hash,
    ) = load_module(obj_path)
    if (3, 3) <= version_tuple <= (3, 7):
        statinfo = os.stat(load_py)
        assert statinfo.st_size == source_size
        assert sip_hash is None
    elif version_tuple < (3, 3):
        assert source_size is None, source_size
        assert sip_hash is None

    for field in CodeTypeUnionFields:
        if hasattr(co_file, field):
            if field == "co_code" and (pypy or IS_PYPY):
                continue
            load_file_field = getattr(co_file, field)
            load_module_field = getattr(co_module, field)
            assert (
                load_module_field == load_file_field
            ), "field %s\nmodule:\n\t%s\nfile:\n\t%s" % (
                field,
                load_module_field,
                load_file_field,
            )
            print("ok %s" % field)


if __name__ == "__main__":
    test_load_file()
