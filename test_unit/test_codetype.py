"""
Check interoperability of native an emulated code type.
"""
import types
import xdis.codetype
import unittest


def five():
    return 5

class Offset2LineTests(unittest.TestCase):

    def test_codeType2Portable(self):
        if hasattr(five, "__code__"):
            # Python 2.6+
            five_code = five.__code__
        elif hasattr(five, "func_code"):
            # Python 2.6-
            five_code = five.func_code

        cc = xdis.codetype.codeType2Portable(five_code)
        self.assertEqual(xdis.codetype.portableCodeType(), type(cc))
        new_code = cc.to_native()
        self.assertEqual(types.CodeType, type(new_code))
        self.assertEqual(eval(new_code), 5)
        cc_new = cc.replace(co_name="five_renamed")
        self.assertEqual(cc_new.co_name, "five_renamed")
        self.assertEqual(eval(cc_new.to_native()), 5)


if __name__ == "__main__":
    unittest.main()
