from dis import findlabels as findlabels_std

from xdis.cross_dis import findlabels
from xdis.op_imports import get_opcode_module
from xdis.version_info import IS_GRAAL, PYTHON_IMPLEMENTATION, PYTHON_VERSION_TRIPLE


def test_findlabels():
    code = findlabels.__code__.co_code
    opc = get_opcode_module(PYTHON_VERSION_TRIPLE, PYTHON_IMPLEMENTATION)

>>>>>>> python-3.3-to-3.5
    assert findlabels(code, opc) == findlabels_std(code)


if __name__ == "__main__":
    test_findlabels()
