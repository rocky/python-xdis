from xdis import IS_PYPY, PYTHON_VERSION
from xdis.main import get_opcode
from xdis.op_imports import get_opcode_module
from xdis.cross_dis import op_has_argument, xstack_effect
import dis

def test_opcode():
    opc = get_opcode(PYTHON_VERSION, IS_PYPY)
    opmap = dict([(k.replace('+', '_'), v)
                  for (k, v) in dis.opmap.items()])

    print("Extra in dis:", set(opmap.items()) - set(opc.opmap.items()))
    print("Extra in xdis:", set(opc.opmap.items()) - set(opmap.items()))

    for item in opmap.items():
        assert item in opc.opmap.items(), item

    fields_str = "hascompare hasconst hasfree hasjabs hasjrel haslocal"
    # PyPy 2.7.13 changes opcodes mid-version. It is too complicated
    # to figure out where the change actually occurred
    # Pypy 3.6.9 may or may not have JUMP_IF_NOT_DEBUG
    if not (IS_PYPY and PYTHON_VERSION in (2.7, 3.6)):
        assert all(item in opmap.items() for item in opc.opmap.items())
    elif (IS_PYPY and PYTHON_VERSION == 3.6):
        # Don't count JUMP_IF_NOT_DEBUG mismatch
        fields_str = "hascompare hasconst hasfree hasjabs haslocal"

    assert all(item in opc.opmap.items() for item in opmap.items())

    fields = fields_str.split()
    for field in fields:
        opc_set = set(getattr(opc, field))
        dis_set = set(getattr(dis, field))
        assert opc_set == dis_set, \
            ("diff in %s: %s" %
             (field, ', '.join([opc.opname[i]
                                         for i in list(opc_set ^ dis_set)])))

def test_stack_effect():
    if PYTHON_VERSION < 3.4:
        # TODO figure out some other kind if internal checks to tod.
        print("Skipped for now - need to figure out how to test")
        return

    if IS_PYPY:
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
        if (
            PYTHON_VERSION > 3.7
            and opcode in opc.CONDITION_OPS
            and opname not in ("JUMP_IF_FALSE_OR_POP",
                               "JUMP_IF_TRUE_OR_POP",
                               "POP_JUMP_IF_FALSE",
                               "POP_JUMP_IF_TRUE",
                               "SETUP_FINALLY",)
        ):
            xdis_args.append(0)
            dis_args.append(0)

        effect = xstack_effect(*xdis_args)
        check_effect = dis.stack_effect(*dis_args)
        assert effect != -100, (
            "%d (%s) needs adjusting; should be: should have effect %d"
            % (opcode, opname, check_effect)
        )
        assert check_effect == effect, (
            "%d (%s) not okay; effect %d vs %d"
            % (opcode, opname, effect, check_effect)
        )
        print("%d (%s) is good: effect %d" % (opcode, opname, effect))
        pass
    return

if __name__ == "__main__":
    test_opcode()
    test_stack_effect()
