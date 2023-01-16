import unittest
import dis
import sys
import os.path as osp
from xdis import get_opcode
from xdis.op_imports import get_opcode_module
from xdis.version_info import version_tuple_to_str
from xdis.cross_dis import op_has_argument, xstack_effect
import xdis

def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()
opcode_stack_effect = [-100]*256

class OpcodeTests(unittest.TestCase):
    def test_stack_effect_fixed(self):
        """Check stack effect of opcodes that don't vary in the stack effect.
        This we get from tables that are derived the Python Interpreter C source.
        Thanks are to the Maynard project for this idea.
        """
        versions = ((2, 6), (2, 7),
                    (3, 1), (3, 2), (3, 3),
                    (3, 4), (3, 5), (3, 6), (3, 7),
                    (3, 8), )
        for version in versions:
            v_str = "%s%s" % (version[0], version[1])
            opc = get_opcode(version, False)
            se_file_py = osp.realpath(osp.join(srcdir, "..", "pytest", "stackeffect", "se%s.py" % v_str))
            opcode_stack_effect = eval(open(se_file_py).read())
            self.assertEqual(len(opcode_stack_effect), 256)

            for opcode in range(256):
                check_effect = opcode_stack_effect[opcode]
                if check_effect == -100:
                    continue

                opname = opc.opname[opcode]
                # FIXME: not sure what's up with these in 2.6
                if opname.startswith("SLICE"):
                    continue

                if op_has_argument(opcode, opc):
                    effect = xstack_effect(opcode, opc, 10)
                else:
                    effect = xstack_effect(opcode, opc)

                pass

            for opname, opcode, in opc.opmap.items():
                if op_has_argument(opcode, opc):
                    continue
                # These are are not in the C code although they are documented as opcodes
                elif opname in ("STOP_CODE", "NOP"):
                    continue
                # FIXME: not sure what's up with these in 2.6
                elif opname.startswith("SLICE"):
                    continue

                effect = xstack_effect(opcode, opc)
                check_effect = opcode_stack_effect[opcode]
                self.assertEqual(check_effect, effect, (
                    "in version %s %s (%s) not okay; effect xstack_effect is %d; C source has %d"
                    % (version_tuple_to_str(opc.version_tuple), opcode, opname, effect, check_effect))
                )
                # print("version %s: %d (%s) is good: effect %d" % (version, opcode, opname, effect))
                pass
            pass
        return


if __name__ == '__main__':
    unittest.main()
