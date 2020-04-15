import types
import xdis.codetype
def five():
    return 5

def test_codeType2Portable():
    cc = xdis.codetype.codeType2Portable(five.__code__)
    assert xdis.codetype.portableCodeType() == type(cc)
    new_code = cc.to_native()
    assert types.CodeType == type(new_code)
    assert eval(new_code) == 5

if __name__ == "__main__":
    test_codeType2Portable()
