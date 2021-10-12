#!/usr/bin/env python

import os

from xdis.load import load_module
from xdis import PYTHON_VERSION_TRIPLE

import unittest

if PYTHON_VERSION_TRIPLE < (2, 4):
    from sets import Set as set
    frozenset = set

def get_srcdir():
    filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(filename)

srcdir = get_srcdir()

class MarshalTest(unittest.TestCase):

    def test_basic(self):
        """Tests xdis.load.load_module"""
        # We deliberately pick a bytecode that we aren't likely to be running against
        mod_file = os.path.join(get_srcdir(), '..', 'test', 'bytecode_2.5',
                            '02_complex.pyc')

        (version, timestamp, magic_int, co, is_pypy,
         source_size, sip_hash) = load_module(mod_file)
        self.assertEqual(version[:2], (2, 5),
                         "Should have picked up Python version properly")
        self.assertEqual(co.co_consts, (5j, None), "Code should have a complex constant")

        mod_file = os.path.join(get_srcdir(), '..', 'test', 'bytecode_3.3',
                            '06_frozenset.pyc')
        (version, timestamp, magic_int, co, is_pypy,
         source_size, sip_hash) = load_module(mod_file)
        expect = (0, None, 'attlist', 'linktype', 'link', 'element', 'Yep',
                      frozenset(['linktype', 'attlist', 'element', 'link']))
        self.assertEqual(co.co_consts, expect, "Should handle frozenset")

# if __name__ == "__main__":
#     unittest.main()
