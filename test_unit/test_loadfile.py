#!/usr/bin/env python
import os, sys, unittest
from xdis.load import load_file, check_object_path, load_module
from xdis import IS_PYPY

class TestLoad(unittest.TestCase):

    def test_basic(self):
        """Basic test of load_file, check_object_path and load_module"""
        filename = __file__
        if filename.endswith('.pyo') or filename.endswith('.pyc'):
            filename = filename[:-1]
        co = load_file(filename)
        obj_path = check_object_path(__file__)
        if os.path.exists(obj_path):
            (version, timestamp, magic_int, co2, is_pypy,
             source_size) = load_module(obj_path)
            self.assertEqual(sys.version[0:3], str(version))
            if IS_PYPY:
                self.assertTrue("Skipped until we get better code comparison on PYPY")
            else:
                for attr in """co_filename co_names co_flags co_argcount
                             co_varnames""".split():
                    self.assertEqual(getattr(co, attr), getattr(co2, attr), attr)
        else:
            self.assertTrue("Skipped because we can't find %s" % obj_path)

if __name__ == '__main__':
    unittest.main()
