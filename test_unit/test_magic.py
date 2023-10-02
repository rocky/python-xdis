import sys
import unittest
from xdis.version_info import IS_PYPY, version_tuple_to_str
import xdis.magics as magics

class TestMagics(unittest.TestCase):

    def test_basic(self):
        """Basic test of magic numbers"""
        if hasattr(sys, 'version_info'):
            version = version_tuple_to_str()
            if IS_PYPY:
                version += 'pypy'
            self.assertTrue(version in magics.magics.keys(),
                            "version %s is not in magic.magics.keys: %s" %
                            (version, magics.magics.keys()))

        self.assertEqual(magics.MAGIC, magics.int2magic(magics.magic2int(magics.MAGIC)))

        if not (3, 5, 2) <= sys.version_info < (3, 6, 0):
            self.assertEqual(magics.sysinfo2magic(), magics.MAGIC,
                            "magic from imp.get_magic() for %s "
                            "should be sysinfo2magic()" % version_tuple_to_str())


if __name__ == '__main__':
    unittest.main()
