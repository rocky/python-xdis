import sys
import dis
import unittest
import xdis.std as xdis
from xdis.version_info import version_tuple_to_str


class TestModules(unittest.TestCase):
    def test_basic(self):
        # test all ops match
        if hasattr(sys, "version_info"):
            print("Testing Python Version : %s" % version_tuple_to_str())
        try:
            self.assertEqual(dis.opname, xdis.opname)
        except AssertionError:
            if len(dis.opname) != len(xdis.opname):
                print("Opname table length mismatch between dis and xdis")
                print("OPNAME TABLE LENGTH MISMATCH, LONGER TABLE WILL BE TRUNCATED")
                raise AssertionError
            for index, (dop, xop) in enumerate(zip(dis.opname, xdis.opname)):
                if dop != xop:
                    print("-"*20)
                    print("Mismatch at op %s" % index)
                    print("dis opname  : %s" % dop)
                    print("xdis opname : %s" % xop)
            raise AssertionError

        # test "has.." tables
        xmod = xdis.get_opcode_module()
        attrs = (attr for attr in dir(dis) if attr.startswith("has"))
        for attr in attrs:
            try:
                self.assertEqual(sorted(getattr(dis, attr)), sorted(getattr(xmod, attr)))
            except AssertionError:
                print("Mismatch 'has' table : %s" % attr)
                print(sorted(getattr(dis, attr)))
                print(sorted(getattr(xmod, attr)))
                raise AssertionError

if __name__ == "__main__":
    unittest.main()
