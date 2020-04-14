# (C) Copyright 2020 by Rocky Bernstein
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

__docformat__ = "restructuredtext"
from xdis.codetype.base import *
from xdis.codetype.code14 import *
from xdis.codetype.code2 import *
from xdis.codetype.code3 import *
from xdis.codetype.code38 import *

import types
from xdis.version_info import PYTHON3, PYTHON_VERSION

def CodeType2XdisCode(code):
    """Converts a native types.CodeType code object into a the
corresponding more flexible xdis Code type,.
    """
    if not isinstance(code, types.CodeType):
        raise TypeError("paramater expected to be a types.CodeType type; is %s instead" %
                        type(code))
    if PYTHON_VERSION >= 3.0:
        if PYTHON_VERSION < 3.8:
            return Code3(
                co_argcount,
                co_kwonlyargcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                co_consts,
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_firstlineno,
                co_lnotab,
                co_freevars,
                co_cellvars
            )
        else:
            return Code38(
                co_argcount,
                co_posonlyargcount, # Not in < 3.8
                co_kwonlyargcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                co_consts,
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_firstlineno,
                co_lnotab,
                co_freevars,
                co_cellvars,
                co_argcount,
            )
    elif PYTHON_VERSION < 2.0:
        # 1.x .. 1.5
        if PYTHON_VERSION < 1.5:
            return Code14(
                co_argcount,
                co_kwonlyargcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                co_consts,
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_lnotab,
                co_freevars,
                co_cellvars
                )
        else:
            return Code15(
                co_argcount,
                co_kwonlyargcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                co_consts,
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_firstlineno,
                co_lnotab,
                co_freevars,
                co_cellvars
                )

    else:
        # 2.0 .. 2.7
        return Code2(
            co_argcount,
            co_nlocals,
            co_stacksize,
            co_flags,
            co_code,
            co_consts,
            co_names,
            co_varnames,
            co_filename,
            co_name,
            co_firstlineno, # Not in 1.x
            co_lnotab,
            co_freevars,
            co_cellvars
        )
