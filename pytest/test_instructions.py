"""xdis.bytecode testing"""
import sys
from xdis.op_imports import get_opcode_module
from xdis import IS_PYPY
from xdis.version_info import PYTHON_VERSION_TRIPLE
import pytest

def extended_arg_fn36():
    if __file__:
        return 0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0+0
    return 3

#  Bytecode that has a single conditional jump forward and an unconditional jump backwards
def loop():
    x = False
    while x:
        x = True
    return x

from xdis.bytecode import Bytecode

pytest.mark.skipif(PYTHON_VERSION_TRIPLE < (3, 6),
                    reason="asssume Python 3.6 or greater wordsize instructions")
def test_inst_size():
    if (PYTHON_VERSION_TRIPLE[:2] == (3,6)) and not IS_PYPY:
        opc = get_opcode_module(sys.version_info)
        bytecode_obj = Bytecode(extended_arg_fn36, opc)
        instructions = list(bytecode_obj.get_instructions(extended_arg_fn36))

        inst1 = instructions[1]
        assert inst1.opname == 'EXTENDED_ARG'
        assert inst1.argval == 0

        inst2 = instructions[2]
        assert inst2.opname == 'POP_JUMP_IF_FALSE'
        assert inst2.has_extended_arg == True
        assert inst2.inst_size == 4

        # for inst in instructions:
        #     print(inst)
    else:
        assert True

pytest.mark.skipif(PYTHON_VERSION_TRIPLE < (2, 7),
                    reason="asssume Python 2.7 or greater")
def test_inst_jumps():
    if (sys.version_info >= (2,7)):
        variant = 'pypy' if IS_PYPY else None
        opc = get_opcode_module(sys.version_info, variant)
        bytecode_obj = Bytecode(extended_arg_fn36, opc)
        instructions = list(bytecode_obj.get_instructions(loop))
        seen_pjif = False
        seen_ja = False
        for inst in instructions:
            if inst.opname == "POP_JUMP_IF_FALSE":
                assert inst.is_jump()
                seen_pjif = True
            elif inst.opname == "JUMP_ABSOLUTE":
                assert inst.is_jump()
                assert not inst.jumps_forward()
                seen_ja = True
                pass
            pass
        assert seen_pjif
        # Python 3.10 code generation is more efficient and doesn't
        # and removes a JUMP_ABSOLUTE.
        if PYTHON_VERSION_TRIPLE < (3, 10):
            assert seen_ja

if __name__ == '__main__':
    test_inst_jumps()
