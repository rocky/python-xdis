import xdis.codetype
def five():
    return 5

def test_CodeType2XdisCode():
    cc = xdis.codetype.CodeType2XdisCode(five.__code__)
    new_code = cc.to_native()
    assert eval(new_code) == 5

if __name__ == "__main__":
    test_CodeType2XdisCode()
