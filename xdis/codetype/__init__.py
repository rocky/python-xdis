# (C) Copyright 2020-2021 by Rocky Bernstein
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

from xdis.namedtuple24 import namedtuple
from xdis.codetype.base import *
from xdis.codetype.code13 import *
from xdis.codetype.code15 import *
from xdis.codetype.code20 import *
from xdis.codetype.code30 import *
from xdis.codetype.code38 import *

import types
from xdis.version_info import PYTHON_VERSION_TRIPLE


def codeType2Portable(code, version_tuple=PYTHON_VERSION_TRIPLE):
    """Converts a native types.CodeType code object into a the
    corresponding more flexible xdis Code type,.
    """
    if isinstance(code, CodeBase):
        return code
    if not (isinstance(code, types.CodeType) or isinstance(code, CodeTypeUnion)):
        raise TypeError(
            "parameter expected to be a types.CodeType type; is %s instead" % type(code)
        )
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
                code.co_lnotab,
                code.co_freevars,
                code.co_cellvars,
            )
        else:
            return Code38(
                code.co_argcount,
                code.co_posonlyargcount,  # Not in < 3.8
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
                code.co_lnotab,
                code.co_freevars,
                code.co_cellvars,
            )
    elif version_tuple > (2, 0):
        # 2.0 .. 2.7
        return Code2(
            code.co_argcount,
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
            code.co_lnotab,
            code.co_freevars,  # not in 1.x
            code.co_cellvars,  # not in 1.x
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
                code.co_lnotab,  # Not in 1.0..1.4
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
        else:
            # 3.8 ..
            return Code38
    elif version_tuple > (2, 0):
        # 2.0 .. 2.7
        return Code2
    else:
        # 1.0 .. 1.5
        if version_tuple <= (1, 3):
            return Code13
        else:
            return Code15
    raise RuntimeError("Implementation bug: can't handle version %s" % version)


# In contrast to Code3, Code2, etc. you can use CodeTypeUnint for building
# an incomplete code type, which might be converted to another code type
# later.
CodeTypeUnionFields = Code38FieldNames.split()
CodeTypeUnion = namedtuple("CodeTypeUnion", CodeTypeUnionFields)


# Note: default values of `None` indicate a required parameter.
# default values of -1, (None,) or "" indicate an unsupplied parameter.
def to_portable(
    co_argcount,
    co_posonlyargcount=-1,  # 3.8+
    co_kwonlyargcount=-1,  # 3.0+
    co_nlocals=None,
    co_stacksize=-1,  # 1.5+
    co_flags=None,
    co_code=None,  # 3.0+ this type changes from <str> to <bytes>
    co_consts=None,
    co_names=None,
    co_varnames=None,
    co_filename=None,
    co_name=None,
    co_firstlineno=-1,
    co_lnotab="",  # 1.5+; 3.0+ this type changes from <str> to <bytes>
    co_freevars=(None,),  # 2.0+
    co_cellvars=(None,),  # 2.0+
    version_triple=PYTHON_VERSION_TRIPLE,
):
    code = CodeTypeUnion(
        co_argcount,
        co_posonlyargcount,
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
    )
    return codeType2Portable(code, version_triple)


if __name__ == "__main__":
    x = codeType2Portable(to_portable.__code__)
    print(x)
