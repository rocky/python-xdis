import dis

import pytest
from xdis import get_opcode
from xdis.version_info import (
    IS_GRAAL,
    IS_PYPY,
    PYTHON_IMPLEMENTATION,
    PYTHON_VERSION_TRIPLE,
)


@pytest.mark.skipif(
    PYTHON_VERSION_TRIPLE >= (3, 14),
    reason="Python >= 3.14 is not complete.",
)
@pytest.mark.skipif(
    IS_GRAAL, reason="Graal's `dis' module lies about its opcodes."
)
def test_opcode() -> None:
    opc = get_opcode(PYTHON_VERSION_TRIPLE, PYTHON_IMPLEMENTATION)
    opmap = dict([(k.replace("+", "_"), v) for (k, v) in dis.opmap.items()])
    #        (2, 7),
    #        (3, 6),
    #        (3, 7),
    #        (3, 8),
    #        (3, 9),

    native_opmaps = set(opmap.items())
    if native_opmaps - set(opc.opmap.items()):
        print("Extra opmap items in dis:", native_opmaps - set(opc.opmap.items()))

    if IS_PYPY:
        for extra_opcode_tuple in (("LOAD_REVDB_VAR", 205),):
            if extra_opcode_tuple not in native_opmaps:
                native_opmaps.add(extra_opcode_tuple)
                pass
            pass

        if PYTHON_VERSION_TRIPLE < (3, 7):
            for extra_opcode_tuple in (("JUMP_IF_NOT_DEBUG", 204),):
                if extra_opcode_tuple not in native_opmaps:
                    native_opmaps.add(extra_opcode_tuple)
                    pass
                pass
            pass
        elif PYTHON_VERSION_TRIPLE[:2] == (3, 7):
            for extra_opcode_tuple in (("STORE_ANNOTATION", 127),):
                if extra_opcode_tuple not in native_opmaps:
                    native_opmaps.add(extra_opcode_tuple)
                    pass
                pass

    if set(opc.opmap.items()) - native_opmaps:
        print("Extra opmap items in xdis:", set(opc.opmap.items()) - native_opmaps)

    for item in native_opmaps:
        assert item in opc.opmap.items(), item

    assert all(item in opc.opmap.items() for item in native_opmaps)

    fields_str = "hascompare hasconst hasfree hasjabs hasjrel haslocal"

    assert all(item in native_opmaps for item in opc.opmap.items())
    fields_str = "hascompare hasconst hasfree hasjabs haslocal"

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
