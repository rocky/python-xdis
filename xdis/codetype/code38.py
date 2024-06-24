# (C) Copyright 2020-2021, 2023-2024 by Rocky Bernstein
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

import types
from copy import deepcopy

from xdis.codetype.code30 import Code3, Code3FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

# Note: order is the positional order. It is important to match this
# with the 3.8 order.
Code38FieldNames = """
        co_argcount
        co_posonlyargcount
        co_kwonlyargcount
        co_nlocals
        co_stacksize
        co_flags
        co_code
        co_consts
        co_names
        co_varnames
        co_freevars
        co_cellvars
        co_filename
        co_name
        co_firstlineno
        co_lnotab
"""

Code38FieldTypes = deepcopy(Code3FieldTypes)
Code38FieldTypes.update(
    {
        "co_posonlyargcount": int,
    }
)


class Code38(Code3):
    """
    Class for a Python 3.8..3.9 code object used when a Python
    interpreter less not in that range but working on Python 3.8..3.10
    bytecode. It also functions as an object that can be used to build
    or write a Python3 code object, since we allow mutable structures.

    When done mutating, call method to_native().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise, the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.

    """

    def __init__(
        self,
        co_argcount: int,
        co_posonlyargcount: int,
        co_kwonlyargcount: int,
        co_nlocals: int,
        co_stacksize: int,
        co_flags,
        co_code,
        co_consts,
        co_names,
        co_varnames,
        co_filename,
        co_name: str,
        co_firstlineno: int,
        co_lnotab,
        co_freevars,
        co_cellvars,
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super(Code38, self).__init__(
            co_argcount=co_argcount,
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
            co_firstlineno=co_firstlineno,
            co_lnotab=co_lnotab,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
        )
        self.co_posonlyargcount = co_posonlyargcount
        self.fieldtypes = Code38FieldTypes
        if type(self) == Code38:
            self.check()

    def to_native(self) -> types.CodeType:
        if not (3, 8) <= PYTHON_VERSION_TRIPLE < (3, 10):
            raise TypeError(
                "Python Interpreter needs to be in range 3.8..3.9; "
                f"is {version_tuple_to_str()}"
            )

        code = deepcopy(self)
        code.freeze()
        try:
            code.check()
        except AssertionError as e:
            raise TypeError(e)

        return types.CodeType(
            code.co_argcount,
            code.co_posonlyargcount,
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
            code.co_lnotab,  # noqa
            code.co_freevars,
            code.co_cellvars,
        )
