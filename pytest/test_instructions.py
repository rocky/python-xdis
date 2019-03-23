"""xdis.bytecode testing"""
import sys
from xdis.op_imports import get_opcode_module
from xdis import IS_PYPY
import pytest

def extended_arg_fn36():
    if __file__:
        return 0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0
    return 3

from xdis.bytecode import Bytecode

pytest.mark.skipif(sys.version_info < (3,6),
                    reason="asssume Python 3.6 or greater wordsize instructions")
def test_inst_size():
    if (sys.version_info >= (3,6)):
        variant = 'pypy' if IS_PYPY else None
        opc = get_opcode_module(sys.version_info, variant)
        bytecode_obj = Bytecode(extended_arg_fn36, opc)
        instructions = list(bytecode_obj.get_instructions(extended_arg_fn36))

        inst1 = instructions[1]
        assert inst1.opname == 'EXTENDED_ARG'
        assert inst1.argval == 0

        inst2 = instructions[2]
        assert inst2.opname == 'POP_JUMP_IF_FALSE'
        assert inst2.has_extended_arg == True
        assert inst2.inst_size == 4
    else:
        assert True

    # for inst in instructions:
    #    print(inst)
