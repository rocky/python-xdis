#!/usr/bin/env python
"""
This is a translation into Python of the seXY.c programs.
However this can only used in Python 3.4 and above which has dis.stack_effect().
"""
from xdis import PYTHON_VERSION
import dis
NOTFIXED = -100
from xdis.cross_dis import op_has_argument
from xdis import get_opcode

print("# Python %s Stack effects\n" % PYTHON_VERSION)
assert PYTHON_VERSION >= 3.4, "This only works for Python version 3.4 and above; you have version %s." % PYTHON_VERSION
print("[");
opc = get_opcode(PYTHON_VERSION, False)
for i in range(256):
    try:
        if op_has_argument(i, opc):
            effect = dis.stack_effect(i, 0)
            opargs_to_try = [ -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 256, 1000, 0xffff, 0 ]
            for operand in opargs_to_try:
                with_oparg = dis.stack_effect(i, operand)
                if effect != with_oparg:
                    effect = NOTFIXED
                    break
                pass
        else:
            effect = dis.stack_effect(i)
            pass
        pass
    except:
        print("  %d, # %d" % (NOTFIXED, i))
        continue

    if effect != NOTFIXED:
        print("  %4d, # %d," % (effect, i))
    else:
        print("  %d, # %d" % (NOTFIXED, i))
        pass
    pass

print("]")
