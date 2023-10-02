# (C) Copyright 2017, 2021, 2023 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
PYPY 2.6 opcodes

This is a like Python 2.6's opcode.py with some classification
of stack usage.
"""

import xdis.opcodes.opcode_26 as opcode_26
from xdis.opcodes.base import (
    finalize_opcodes,
    init_opdata,
    jrel_op,
    name_op,
    nargs_op,
    update_pj2,
    varargs_op,
)
from xdis.opcodes.format.extended import (
    extended_format_ATTR,
    extended_format_RETURN_VALUE,
)

version_tuple = (2, 6)
python_implementation = "PyPy"

loc = locals()
init_opdata(loc, opcode_26, version_tuple, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# fmt: off
# PyPy only
# ----------
name_op(loc,   'LOOKUP_METHOD',   201,  1, 2)
nargs_op(loc,  'CALL_METHOD',     202, -1, 1)
# fmt: on

loc["hasnargs"].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(loc, "BUILD_LIST_FROM_ARG", 203)

# Used only in assert statements
jrel_op(loc, "JUMP_IF_NOT_DEBUG", 204, conditional=True)

opcode_extended_fmt = {
    "LOAD_ATTR": extended_format_ATTR,
    "RETURN_VALUE": extended_format_RETURN_VALUE,
    "STORE_ATTR": extended_format_ATTR,
}

# FIXME remove (fix uncompyle6)
update_pj2(globals(), loc)
finalize_opcodes(loc)
