import unittest, imp, sys
from xdis import PYTHON_VERSION
import xdis.magics as magics

class TestOpcodes(unittest.TestCase):

    def test_basic(self):
        """Basic test of magic numbers"""
        current = imp.get_magic()
        if hasattr(sys, 'version_info'):
            version = '.'.join([str(v) for v in sys.version_info[0:3]])
            self.assertTrue(version in magics.magics.keys(),
                            "version %s is not in magic.magics.keys: %s" %
                            (version, magics.magics.keys()))

        self.assertEqual(current, magics.int2magic(magics.magic2int(current)))
        self.assertTrue(str(PYTHON_VERSION) in magics.magics.keys(),
                        "PYTHON VERSION %s is not in magic.magics.keys: %s" %
                        (PYTHON_VERSION, magics.magics.keys()))

if __name__ == '__main__':
    unittest.main()
