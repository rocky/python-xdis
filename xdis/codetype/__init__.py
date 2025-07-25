# (C) Copyright 2020-2021, 2023-2025 by Rocky Bernstein
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

import types
from collections import namedtuple
from typing import Optional

from xdis.codetype.base import CodeBase
from xdis.codetype.code13 import Code13
from xdis.codetype.code15 import Code15
from xdis.codetype.code20 import Code2
from xdis.codetype.code30 import Code3
from xdis.codetype.code38 import Code38
from xdis.codetype.code310 import Code310
from xdis.codetype.code311 import Code311, Code311FieldNames
from xdis.version_info import IS_PYPY, PYTHON_VERSION_TRIPLE


def codeType2Portable(code, version_tuple=PYTHON_VERSION_TRIPLE):
    """Converts a native types.CodeType code object into a
    corresponding more flexible xdis Code type.
    """
    if isinstance(code, CodeBase):
        return code
    if not (isinstance(code, types.CodeType) or isinstance(code, CodeTypeUnion)):
        raise TypeError(
            f"parameter expected to be a types.CodeType type; is {type(code)} instead"
        )
    line_table_field = "co_lnotab" if hasattr(code, "co_lnotab") else "co_linetable"
    line_table = getattr(code, line_table_field)
    if version_tuple >= (3, 0):
        if version_tuple < (3, 8):
            return Code3(
                code.co_argcount,
                code.co_kwonlyargcount,
                code.co_nlocals,
                code.co_stacksize,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
                code.co_firstlineno,
                line_table,
                code.co_freevars,
                code.co_cellvars,
            )
        elif version_tuple < (3, 10):
            return Code38(
                co_argcount=code.co_argcount,
                co_posonlyargcount=code.co_posonlyargcount,
                co_kwonlyargcount=code.co_kwonlyargcount,
                co_nlocals=code.co_nlocals,
                co_stacksize=code.co_stacksize,
                co_flags=code.co_flags,
                co_code=code.co_code,
                co_consts=code.co_consts,
                co_names=code.co_names,
                co_varnames=code.co_varnames,
                co_freevars=code.co_freevars,
                co_cellvars=code.co_cellvars,
                co_filename=code.co_filename,
                co_name=code.co_name,
                co_firstlineno=code.co_firstlineno,
                co_lnotab=line_table,
            )
        elif version_tuple[:2] == (3, 10) or IS_PYPY and version_tuple[:2] == (3, 11):
            return Code310(
                co_argcount=code.co_argcount,
                co_posonlyargcount=code.co_posonlyargcount,
                co_kwonlyargcount=code.co_kwonlyargcount,
                co_nlocals=code.co_nlocals,
                co_stacksize=code.co_stacksize,
                co_flags=code.co_flags,
                co_code=code.co_code,
                co_consts=code.co_consts,
                co_names=code.co_names,
                co_varnames=code.co_varnames,
                co_freevars=code.co_freevars,
                co_cellvars=code.co_cellvars,
                co_filename=code.co_filename,
                co_name=code.co_name,
                co_firstlineno=code.co_firstlineno,
                co_linetable=line_table,
            )
        elif version_tuple[:2] >= (3, 11):
            return Code311(
                co_argcount=code.co_argcount,
                co_posonlyargcount=code.co_posonlyargcount,
                co_kwonlyargcount=code.co_kwonlyargcount,
                co_nlocals=code.co_nlocals,
                co_stacksize=code.co_stacksize,
                co_flags=code.co_flags,
                co_consts=code.co_consts,
                co_code=code.co_code,
                co_names=code.co_names,
                co_varnames=code.co_varnames,
                co_freevars=code.co_freevars,
                co_cellvars=code.co_cellvars,
                co_filename=code.co_filename,
                co_name=code.co_name,
                co_qualname=code.co_qualname,
                co_firstlineno=code.co_firstlineno,
                co_linetable=line_table,
                co_exceptiontable=code.co_exceptiontable,
            )
    elif version_tuple > (2, 0):
        # 2.0 .. 2.7
        return Code2(
            co_argcount=code.co_argcount,
            co_nlocals=code.co_nlocals,
            co_stacksize=code.co_stacksize,
            co_flags=code.co_flags,
            co_code=code.co_code,
            co_consts=code.co_consts,
            co_names=code.co_names,
            co_varnames=code.co_varnames,
            co_filename=code.co_filename,
            co_name=code.co_name,
            co_firstlineno=code.co_firstlineno,
            co_lnotab=line_table,
            co_freevars=code.co_freevars,  # not in 1.x
            co_cellvars=code.co_cellvars,  # not in 1.x
        )
    else:
        # 1.0 .. 1.5
        if version_tuple < (1, 5):
            # 1.0 .. 1.3
            return Code13(
                code.co_argcount,
                code.co_nlocals,
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
            )
        else:
            return Code15(
                code.co_argcount,
                code.co_nlocals,
                code.co_stacksize,  # not in 1.0..1.4
                code.co_flags,
                code.co_code,
                code.co_consts,
                code.co_names,
                code.co_varnames,
                code.co_filename,
                code.co_name,
                code.co_firstlineno,  # Not in 1.0..1.4
                line_table,  # Not in 1.0..1.4
            )


def portableCodeType(version_tuple=PYTHON_VERSION_TRIPLE):
    """
    Return the portable CodeType version for the supplied Python release version.
    `version` is a floating-point number, like 2.7, or 3.9. If no version
    number is supplied we'll use the current interpreter version.
    """
    if version_tuple >= (3, 0):
        if version_tuple < (3, 8):
            # 3.0 .. 3.7
            return Code3
        elif version_tuple < (3, 10):
            # 3.8 ... 3.9
            return Code38
        elif version_tuple[:2] == (3, 10) or IS_PYPY and version_tuple[:2] == (3, 11):
            # 3.10
            return Code310
        elif version_tuple[:2] >= (3, 11):
            # 3.11 ...
            return Code311
    elif version_tuple > (2, 0):
        # 2.0 .. 2.7
        return Code2
    else:
        # 1.0 .. 1.5
        if version_tuple <= (1, 3):
            return Code13
        else:
            return Code15


# In contrast to Code3, Code2, etc. you can use CodeTypeUnint for building
# an incomplete code type, which might be converted to another code type
# later.
CodeTypeUnionFields = tuple(Code311FieldNames.split())
CodeTypeUnion = namedtuple("CodeTypeUnion", CodeTypeUnionFields)


# Note: default values of `None` indicate a required parameter.
# default values of -1, (None,) or "" indicate an unsupplied parameter.
def to_portable(
    co_argcount,
    co_posonlyargcount: Optional[int] = -1,  # 3.8 .. 3.10
    co_kwonlyargcount: Optional[int] = -1,  # 3.0+
    co_nlocals=None,
    co_stacksize: Optional[int] = -1,  # 1.5+
    co_flags=None,
    co_code=None,  # 3.0+ this type changes from <str> to <bytes>
    co_consts=None,
    co_names=None,
    co_varnames=None,
    co_filename=None,
    co_name=None,
    co_qualname=None,
    co_firstlineno=-1,
    co_lnotab="",  # 1.5+; 3.0+ this type changes from <str> to <bytes>
    # In 3.11 it is different
    co_freevars=(None,),  # 2.0+
    co_cellvars=(None,),  # 2.0+
    co_exceptiontable=None,  # 3.11+
    version_triple=PYTHON_VERSION_TRIPLE,
):
    code = CodeTypeUnion(
        co_argcount=co_argcount,
        co_posonlyargcount=co_posonlyargcount,
        co_kwonlyargcount=co_kwonlyargcount,
        co_nlocals=co_nlocals,
        co_stacksize=co_stacksize,
        co_flags=co_flags,
        co_code=co_code,
        co_consts=co_consts,
        co_names=co_names,
        co_varnames=co_varnames,
        co_filename=co_filename,
        co_name=co_name,
        co_qualname=co_qualname,
        co_firstlineno=co_firstlineno,
        co_linetable=co_lnotab,
        co_freevars=co_freevars,
        co_cellvars=co_cellvars,
        co_exceptiontable=co_exceptiontable,
    )
    return codeType2Portable(code, version_triple)


if __name__ == "__main__":
    x = codeType2Portable(to_portable.__code__)
    print(x)
