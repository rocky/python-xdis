import unittest, imp
from pyxdis import PYTHON_VERSION
import pyxdis.magics as magics

class TestOpcodes(unittest.TestCase):

    def test_basic(self):
        """Basic test of magic numbers"""
        current = imp.get_magic()
        python_via_magic = magics.by_magic[ current ]
        self.assertEqual(python_via_magic, str(PYTHON_VERSION))

if __name__ == '__main__':
    unittest.main()
