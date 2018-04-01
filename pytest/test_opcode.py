from xdis import IS_PYPY, PYTHON_VERSION
from xdis.main import get_opcode
import dis

def test_opcode():
    opc = get_opcode(PYTHON_VERSION, IS_PYPY)
    opmap = dict([(k.replace('+', '_'), v)
                  for (k, v) in dis.opmap.items()])
    # print(set(opmap.items()) - set(opc.opmap.items()))
    # print(set(opc.opmap.items()) - set(opmap.items()))

    assert all(item in opmap.items() for item in opc.opmap.items())
    assert all(item in opc.opmap.items() for item in opmap.items())

    fields = """hascompare hasconst hasfree hasjabs hasjrel haslocal
    hasname""".split()
    for field in fields:
        opc_set = set(getattr(opc, field))
        dis_set = set(getattr(dis, field))
        assert opc_set == dis_set, \
            ("diff in %s: %s" %
             (field, ', '.join([opc.opname[i]
                                         for i in list(opc_set ^ dis_set)])))
