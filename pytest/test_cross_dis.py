from dis import findlabels as findlabels_std

from xdis.cross_dis import findlabels
from xdis.op_imports import get_opcode_module
from xdis.version_info import IS_GRAAL, PYTHON_VERSION_TRIPLE


@pytest.mark.skipif(IS_GRAAL, reason="Graal label finding is wonky")
@pytest.mark.skipif(
    PYTHON_VERSION_TRIPLE >= (3, 14),
    reason="Python >= 3.14 is not complete.",
)
def test_findlabels():
    code = findlabels.__code__.co_code
    opc = get_opcode_module()
    assert findlabels(code, opc) == findlabels_std(code)


if __name__ == "__main__":
    test_findlabels()
