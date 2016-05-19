#!/usr/bin/env python
import os, sys, unittest
from pyxdis.load import load_file, check_object_path, load_module

class TestLoad(unittest.TestCase):

    def test_basic(self):
        """Basic test of load_file, check_object_path and load_module"""
        co = load_file(__file__)
        obj_path = check_object_path(__file__)
        if os.path.exists(obj_path):
            version, timestamp, magic_int, co2 = load_module(obj_path)
            self.assertEqual(sys.version[0:3], str(version))
            self.assertEqual(co, co2)
        else:
            self.assertTrue("Skipped because we can't find %s" % obj_path)

if __name__ == '__main__':
    unittest.main()
