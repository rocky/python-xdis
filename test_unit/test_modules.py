import sys
import dis
import unittest
import xdis.std as xdis
from xdis.version_info import version_tuple_to_str


class TestModules(unittest.TestCase):
    def test_basic(self):
        # test all ops match
        if hasattr(sys, "version_info"):
            print(f"Testing Python Version : {version_tuple_to_str()}")
        try:
            self.assertEqual(dis.opname, xdis.opname)
        except AssertionError as ae:
            if len(dis.opname) != len(xdis.opname):
                print("Opname table length mismatch between dis and xdis")
                ae.add_note("OPNAME TABLE LENGTH MISMATCH, LONGER TABLE WILL BE TRUNCATED")
            for index, (dop, xop) in enumerate(zip(dis.opname, xdis.opname)):
                if dop != xop:
                    print("-"*20)
                    print(f"Mismatch at op {index}")
                    print(f"dis opname  : {dop}")
                    print(f"xdis opname : {xop}")
            raise ae

        # test "has.." tables
        xmod = xdis.get_opcode_module()
        attrs = (attr for attr in dir(dis) if attr.startswith("has"))
        for attr in attrs:
            try:
                self.assertEqual(sorted(getattr(dis, attr)), sorted(getattr(xmod, attr)))
            except AssertionError as ae:
                ae.add_note(f"Mismatch 'has' table : {attr}")
                raise ae

if __name__ == "__main__":
    unittest.main()
