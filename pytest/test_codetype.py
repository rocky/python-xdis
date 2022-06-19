import types
import xdis.codetype


def five():
    return 5


def test_codeType2Portable():
    if hasattr(five, "__code__"):
        # Python 2.6+
        five_code = five.__code__
    elif hasattr(five, "func_code"):
        # Python 2.6-
        five_code = five.func_code

    cc = xdis.codetype.codeType2Portable(five_code)
    assert xdis.codetype.portableCodeType() == type(cc)
    new_code = cc.to_native()
    assert types.CodeType == type(new_code)
    assert eval(new_code) == 5
    cc_new = cc.replace(co_name="five_renamed")
    assert cc_new.co_name == "five_renamed"
    assert eval(cc_new.to_native()) == 5


if __name__ == "__main__":
    test_codeType2Portable()
