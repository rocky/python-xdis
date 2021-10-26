import unittest, os, sys
from xdis.load import load_file, check_object_path, load_module
from xdis.codetype import CodeTypeUnionFields
from xdis.version_info import IS_PYPY

import os.path as osp


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)

class LoadFileTests(unittest.TestCase):

    def test_load_file(self):
        srcdir = get_srcdir()
        load_py = osp.realpath(osp.join(srcdir, "..", "xdis", "load.py"))

        co_file = load_file(load_py)
        obj_path = check_object_path(load_py)
        (version, timestamp, magic_int, co_module, pypy,
         source_size, sip_hash) = load_module(obj_path)
        if 3.3 <= version <= 3.7:
            statinfo = os.stat(load_py)
            self.assertEqual(statinfo.st_size, source_size)
            self.assertTrue(sip_hash is None)
        elif version < 3.3:
            self.assertTrue(source_size is None, source_size)
            self.assertTrue(sip_hash is None)

        for field in CodeTypeUnionFields:
            if hasattr(co_file, field):
                if field == "co_code" and (pypy or IS_PYPY):
                    continue
                load_file_field = getattr(co_file, field)
                load_module_field = getattr(co_module, field)
                self.assertEqual(load_module_field, load_file_field, (
                    "field %s\nmodule:\n\t%s\nfile:\n\t%s" % (field, load_module_field, load_file_field))
                    )
                #print("ok %s" % field)
                pass
            pass
        return

if __name__ == '__main__':
    unittest.main()
