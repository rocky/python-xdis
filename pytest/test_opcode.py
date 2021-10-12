from xdis import IS_PYPY, PYTHON_VERSION_TRIPLE
from xdis import get_opcode
import dis


def test_opcode():
    opc = get_opcode(PYTHON_VERSION_TRIPLE, IS_PYPY)
    opmap = dict([(k.replace("+", "_"), v) for (k, v) in dis.opmap.items()])

    print("Extra in dis:", set(opmap.items()) - set(opc.opmap.items()))
    print("Extra in xdis:", set(opc.opmap.items()) - set(opmap.items()))

    for item in opmap.items():
        assert item in opc.opmap.items(), item

    fields_str = "hascompare hasconst hasfree hasjabs hasjrel haslocal"
    # PyPy 2.7.13 changes opcodes mid-version. It is too complicated
    # to figure out where the change actually occurred
    # Pypy 3.6.9 may or may not have JUMP_IF_NOT_DEBUG
    if not (IS_PYPY and PYTHON_VERSION_TRIPLE[:2] in ((2, 7), (3, 6), (3, 7))):
        assert all(item in opmap.items() for item in opc.opmap.items())
    elif IS_PYPY and PYTHON_VERSION_TRIPLE[:2] == (3, 6):
        # Don't count JUMP_IF_NOT_DEBUG mismatch
        fields_str = "hascompare hasconst hasfree hasjabs haslocal"

    assert all(item in opc.opmap.items() for item in opmap.items())

    fields = fields_str.split()
    for field in fields:
        opc_set = set(getattr(opc, field))
        dis_set = set(getattr(dis, field))
        assert opc_set == dis_set, "diff in %s: %s" % (
            field,
            ", ".join([opc.opname[i] for i in list(opc_set ^ dis_set)]),
        )


if __name__ == "__main__":
    test_opcode()
