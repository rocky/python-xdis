import unittest, sys
from xdis import PYTHON_VERSION, IS_PYPY
import xdis.magics as magics

class TestMagics(unittest.TestCase):

    def test_basic(self):
        """Basic test of magic numbers"""
        if hasattr(sys, 'version_info'):
            version = '.'.join([str(v) for v in sys.version_info[0:3]])
            if IS_PYPY:
                version += 'pypy'
            self.assertTrue(version in magics.magics.keys(),
                            "version %s is not in magic.magics.keys: %s" %
                            (version, magics.magics.keys()))

        self.assertEqual(magics.MGAIC, magics.int2magic(magics.magic2int(magics.MGAIC)))
        lookup = str(PYTHON_VERSION)
        if IS_PYPY:
            lookup += 'pypy'
        self.assertTrue(lookup in magics.magics.keys(),
                        "PYTHON VERSION %s is not in magic.magics.keys: %s" %
                        (lookup, magics.magics.keys()))

        if not (3, 5, 2) <= sys.version_info < (3, 6, 0):
            self.assertEqual(magics.sysinfo2magic(), magics.MGAIC,
                            "magic from imp.get_magic() for %s "
                            "should be sysinfo2magic()" % lookup)


if __name__ == '__main__':
    unittest.main()
