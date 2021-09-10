import dis
import sys
import os.path as osp
from xdis.op_imports import get_opcode_module
from xdis import get_opcode
from xdis.cross_dis import op_has_argument, xstack_effect
import xdis

def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()
opcode_stack_effect = [-100]*256

def test_stack_effect_fixed():
    """Check stack effect of opcodes that don't vary in the stack effect.
    This we get from tables that are derived the Python Interpreter C source.
    Thanks to the Maynard project for this idea.
    """
    versions = ((2, 5), (2, 6), (2, 7),
                (3, 0), (3, 1), (3, 2), (3, 3),
                (3, 4), (3, 5),
                (3, 6), (3, 7), (3, 8), (3, 9))
    for version in versions:
        v_str = "%s%s" % (version[0], version[1])
        opc = get_opcode(version, False)
        se_file_py = osp.realpath(osp.join(srcdir, "stackeffect", "se%s.py" % v_str))
        opcode_stack_effect = eval(open(se_file_py).read())
        assert len(opcode_stack_effect) == 256

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
            assert check_effect == effect, (
                "in version %s %d (%s) not okay; effect xstack_effect is %d; C source has %d"
                % (opc.version, opcode, opname, effect, check_effect)
            )
            # print("version %s: %d (%s) is good: effect %d" % (version, opcode, opname, effect))
            pass
        pass
    return

def test_stack_effect_vs_dis():

    if xdis.PYTHON_VERSION < 3.4 or xdis.IS_PYPY:
        # TODO figure out some other kind if internal checks to tod.
        print("Skipped for now - need to figure out how to test")
        return

    def test_one(xdis_args, dis_args, has_arg):
        effect = xstack_effect(*xdis_args)
        try:
            check_effect = dis.stack_effect(*dis_args)
        except:
            from trepan.api import debug; debug()
        assert effect != -100, (
            "%d (%s) needs adjusting; should be: should have effect %d"
            % (opcode, opname, check_effect)
        )
        if has_arg:
            op_val = "with operand %d" % dis_args[1]
        else:
            op_val = ""

        assert check_effect == effect, (
            "%d (%s) %s not okay; effect %d vs %d"
            % (opcode, opname, op_val, effect, check_effect)
        )
        print("%d (%s) is good: effect %d" % (opcode, opname, effect))

    if xdis.IS_PYPY:
        variant = "pypy"
    else:
        variant = ""
    opc = get_opcode_module(None, variant)
    for opname, opcode, in opc.opmap.items():
        if opname in ("EXTENDED_ARG", "NOP"):
            continue
        xdis_args = [opcode, opc]
        dis_args = [opcode]

        # TODO: if opcode takes an argument, we should vary the arg and try
        # values in addition to 0 as done below.
        if op_has_argument(opcode, opc):
            xdis_args.append(0)
            dis_args.append(0)
            has_arg = True
        else:
            has_arg = False

        if (
            xdis.PYTHON_VERSION > 3.7
            and opcode in opc.CONDITION_OPS
            and opname not in ("JUMP_IF_FALSE_OR_POP",
                               "JUMP_IF_TRUE_OR_POP",
                               "POP_JUMP_IF_FALSE",
                               "POP_JUMP_IF_TRUE",
                               "SETUP_FINALLY",)
        ):
            xdis_args.append(0)
            dis_args.append(0)

        if has_arg:
            for i in range(0,3):
                dis_args[1] = xdis_args[2] = i
                test_one(xdis_args, dis_args, has_arg)
                pass
            pass
        else:
            test_one(xdis_args, dis_args, has_arg)
        pass
    return


if __name__ == "__main__":
    # test_stack_effect_fixed()
    test_stack_effect_vs_dis()
