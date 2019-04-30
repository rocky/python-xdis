import unittest
from xdis import IS_PYPY, PYTHON_VERSION
from xdis.main import get_opcode
import dis

class TestOpcode(unittest.TestCase):

    def test_opcode(self):
        opc = get_opcode(PYTHON_VERSION, IS_PYPY)
        opmap = dict([(k.replace('+', '_'), v)
                      for (k, v) in dis.opmap.items()])
        # print(set(opmap.items()) - set(l['opmap'].items()))
        # print(set(l['opmap'].items()) - set(opmap.items()))

        for item in opc.opmap.items():
            assert item in opmap.items()
            for item in opmap.items():
                self.assertTrue(item in opc.opmap.items())

        fields = """hascompare hasconst hasfree hasjabs hasjrel haslocal
        hasname""".split()
        for field in fields:
            opc_set = set(getattr(opc, field))
            dis_set = set(getattr(dis, field))
            self.assertTrue(opc_set == dis_set,
                            ("diff in %s: %s" %
                             (field, ', '.join([opc.opname[i]
                                                for i in list(opc_set ^ dis_set)]))))
            pass
        return

if __name__ == '__main__':
    unittest.main()