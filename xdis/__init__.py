"""
  Copyright (c) 2015-2017, 2020 by Rocky Bernstein
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

# Export some functions
from xdis.version_info import *

from xdis.bytecode import (
    Bytecode,
    Instruction,
    extended_arg_val,
    get_jump_targets,
    instruction_size,
    list2bytecode,
    next_offset,
    op_has_argument,
    op_size
    )

from xdis.codetype import (
    Code13,
    Code15,
    Code2,
    Code3,
    Code38,
    code_has_star_star_arg,
    code_has_star_arg,
    iscode,
)

from xdis.load import (
    is_pypy,
    load_file,
    load_module,
    load_module_from_file_object,
    write_bytecode_file,
)

from xdis.magics import (
    int2magic,
    magic2int,
    magic_int2float,
    py_str2float,
    sysinfo2float,
    sysinfo2magic
)
