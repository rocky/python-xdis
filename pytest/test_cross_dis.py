from dis import findlabels as findlabels_std
from xdis.cross_dis import findlabels
from xdis.op_imports import get_opcode_module


def test_findlabels():
    code = findlabels.__code__.co_code
    opc = get_opcode_module()
    assert findlabels(code, opc) == findlabels_std(code)


if __name__ == "__main__":
    test_findlabels()
