# (C) Copyright 2017 by Rocky Bernstein
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
    finalize_opcodes, init_opdata,
    jrel_op, name_op, varargs_op,
    update_pj2
    )

version = 2.6

l = locals()
init_opdata(l, opcode_26, version, is_pypy=True)

# FIXME: DRY common PYPY opcode additions

# PyPy only
# ----------
name_op(l, 'LOOKUP_METHOD',   201,  1, 2)
varargs_op(l,  'CALL_METHOD', 202, -1, 1)
l['hasnargs'].append(202)

# Used only in single-mode compilation list-comprehension generators
varargs_op(l, 'BUILD_LIST_FROM_ARG', 203)

# Used only in assert statements
jrel_op(l, 'JUMP_IF_NOT_DEBUG',      204, conditional=True)

# FIXME remove (fix uncompyle6)
update_pj2(globals(), l)

finalize_opcodes(l)
