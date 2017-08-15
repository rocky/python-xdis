"""Facilitates importing opmaps for the a given Python version"""
import sys
from xdis import IS_PYPY
from xdis.magics import canonic_python_version

from xdis.opcodes import opcode_15 as opcode_15
from xdis.opcodes import opcode_20 as opcode_20
from xdis.opcodes import opcode_21 as opcode_21
from xdis.opcodes import opcode_22 as opcode_22
from xdis.opcodes import opcode_23 as opcode_23
from xdis.opcodes import opcode_24 as opcode_24
from xdis.opcodes import opcode_25 as opcode_25
from xdis.opcodes import opcode_26 as opcode_26
from xdis.opcodes import opcode_27 as opcode_27
from xdis.opcodes import opcode_30 as opcode_30
from xdis.opcodes import opcode_31 as opcode_31
from xdis.opcodes import opcode_32 as opcode_32
from xdis.opcodes import opcode_33 as opcode_33
from xdis.opcodes import opcode_34 as opcode_34
from xdis.opcodes import opcode_35 as opcode_35
from xdis.opcodes import opcode_36 as opcode_36

from xdis.opcodes import opcode_pypy26 as opcode_pypy26
from xdis.opcodes import opcode_pypy27 as opcode_pypy27
from xdis.opcodes import opcode_pypy32 as opcode_pypy32
from xdis.opcodes import opcode_pypy35 as opcode_pypy35

op_imports = {
    '1.5'  : opcode_15,
    1.5    : opcode_15,
    '2.0'  : opcode_20,
    2.0    : opcode_20,
    '2.1'  : opcode_21,
    2.1    : opcode_21,
    '2.2'  : opcode_22,
    2.2    : opcode_22,
    '2.3a0': opcode_23,
    2.3    : opcode_23,
    '2.4b1': opcode_24,
    2.4    : opcode_24,
    '2.5c2': opcode_25,
    2.5:     opcode_25,
    '2.6a1': opcode_26,
    2.6    : opcode_26,
    '2.7'  : opcode_27,
    2.7    : opcode_27,
    '3.0'  : opcode_30,
    3.0    : opcode_30,
    '3.1'  : opcode_31,
    3.1    : opcode_31,
    '3.2'  : opcode_32,
    3.2    : opcode_32,
    '3.3a4': opcode_33,
    3.3    : opcode_33,
    '3.4'  : opcode_34,
    '3.4rc2'  : opcode_34,
    3.4    : opcode_34,
    '3.5'  : opcode_35,
    '3.5.3': opcode_35,
    3.5    : opcode_35,
    '3.6.0rc1': opcode_36,
    3.6    : opcode_36,

    '2.6pypy':  opcode_pypy26,
    '2.7pypy':  opcode_pypy27,
    '3.2pypy':  opcode_pypy32,
    '3.5pypy':  opcode_pypy35,
    }

for k, v in canonic_python_version.items():
    if v in op_imports:
        op_imports[k] = op_imports[v]

def get_opcode_module(version_info=sys.version_info):
    # FIXME: DRY with magics.sysinfo2float()
    vers_str = '.'.join([str(v) for v in version_info[0:3]])
    if version_info[3] != 'final':
        vers_str += '.' + ''.join(version_info)
    if IS_PYPY:
        vers_str += 'pypy'
    return op_imports[canonic_python_version[vers_str]]


if __name__ == '__main__':
    print(get_opcode_module())
