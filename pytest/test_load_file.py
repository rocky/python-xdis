import os
import os.path as osp

import pytest
from xdis import IS_GRAAL, IS_PYPY
from xdis.codetype import CodeTypeUnionFields
from xdis.load import check_object_path, load_file, load_module


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


@pytest.mark.skipif(
    os.name == "nt", reason="Windows differences in output need going over"
)
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

    # FIXME: put in xdis code somewhere
    if IS_GRAAL:
        fields = [
            "co_consts",
            "co_code",
            "co_names",
            "co_varnames",
            "co_freevars",
            "co_cellvars",
            "co_filename",
            "co_name",
            "co_qualname",
            "co_firstlineno",
            "co_lnotab",
            "co_exceptiontable",
        ]
    else:
        fields = CodeTypeUnionFields

    for field in fields:
        if hasattr(co_file, field):
            if field == "co_code" and (pypy or IS_PYPY):
                continue
            load_file_field = getattr(co_file, field)
            load_module_field = getattr(co_module, field)
            if os.name == "windows" and field == "co_filename":
                # MS/Windows is letter case insensitive
                load_module_field = load_module_field.upper()
                load_file_field = load_module_field.upper()
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
