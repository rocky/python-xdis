import unittest, imp
from xdis import PYTHON_VERSION
import xdis.magics as magics

class TestOpcodes(unittest.TestCase):

    def test_basic(self):
        """Basic test of magic numbers"""
        current = imp.get_magic()
        python_via_magic = magics.by_magic[ current ]
        self.assertEqual(python_via_magic[:3], str(PYTHON_VERSION))

if __name__ == '__main__':
    unittest.main()
