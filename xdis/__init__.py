"""
  Copyright (c) 2015-2017, 2020-2021 by Rocky Bernstein
  Copyright (c) 2000 by hartmut Goebel <h.goebel@crazy-compilers.com>

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

  NB. This is not a masterpiece of software, but became more like a hack.
  Probably a complete rewrite would be sensefull. hG/2000-12-27
"""

import sys

__docformat__ = "restructuredtext"

# Export various things from the modules
from xdis.version_info import (
    IS_PYPY,
    PYTHON3,
    PYTHON_VERSION,
    PYTHON_VERSION_STR,
    PYTHON_VERSION_TRIPLE,
)

from xdis.bytecode import (
    Bytecode,
    extended_arg_val,
    get_instructions_bytes,
    list2bytecode,
    next_offset,
    offset2line,
    op_has_argument,
)

from xdis.instruction import Instruction

from xdis.codetype import (
    Code13,
    Code15,
    Code2,
    Code3,
    Code38,
    code_has_star_star_arg,
    code_has_star_arg,
    codeType2Portable,
    iscode,
)

from xdis.cross_dis import (
    code_info,
    extended_arg_val,
    findlinestarts,
    findlabels,
    format_code_info,
    get_code_object,
    get_jump_target_maps,
    instruction_size,
    pretty_flags as pretty_code_flags,
    op_size,
    show_code,
)

from xdis.load import (
    check_object_path,
    is_bytecode_extension,
    is_pypy,
    is_python_source,
    load_file,
    load_module,
    load_module_from_file_object,
    write_bytecode_file,
)

from xdis.lineoffsets import (
    LineOffsetInfo,
    LineOffsets,
    LineOffsetsCompact,
    lineoffsets_in_file,
    lineoffsets_in_module,
)

from xdis.disasm import (
    get_opcode,
    show_module_header,
    disco_loop,
    disco_loop_asm_format,
    disassemble_file,
)

from xdis.opcodes import (
    opcode_13,
    opcode_14,
    opcode_15,
    opcode_22,
    opcode_23,
    opcode_24,
    opcode_25,
    opcode_26,
    opcode_27,
    opcode_30,
    opcode_31,
    opcode_32,
    opcode_33,
    opcode_34,
    opcode_35,
    opcode_36,
    opcode_37,
    opcode_38,
)

from xdis.op_imports import get_opcode_module

from xdis.magics import (
    canonic_python_version,
    int2magic,
    magic2int,
    magic_int2float,
    py_str2float,
    PYTHON_MAGIC_INT,
    sysinfo2float,
    sysinfo2magic,
)

from xdis.util import (
    COMPILER_FLAG_BIT,
    COMPILER_FLAG_NAMES,
    CO_ABSOLUTE_IMPORT,
    CO_ASYNC_GENERATOR,
    CO_COROUTINE,
    CO_FUTURE_BARRY_AS_DBFL,
    CO_FUTURE_DIVISION,
    CO_FUTURE_GENERATOR_STOP,
    CO_FUTURE_PRINT_FUNCTION,
    CO_FUTURE_UNICODE_LITERALS,
    CO_FUTURE_WITH_STATEMENT,
    CO_GENERATOR,
    CO_GENERATOR_ALLOWED,
    CO_ITERABLE_COROUTINE,
    CO_NESTED,
    CO_NEWLOCALS,
    CO_NOFREE,
    CO_OPTIMIZED,
    CO_VARARGS,
    CO_VARKEYWORDS,
    PYPY_COMPILER_FLAG_NAMES,
    code2num,
    co_flags_is_async,
)

# This ensures VERSION will appear in pydoc
from xdis.version import __version__
