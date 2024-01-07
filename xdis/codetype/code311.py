# (C) Copyright 2020-2021, 2023 by Rocky Bernstein
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

from xdis.codetype.code38 import Code38, Code38FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

# Note: order is the positional order given in the Python docs for
# 3.11 types.Codetype.
# "posonlyargcount" is not used, but it is in other Python versions, so it
# has to be included since this structure is used as the Union type
# for all code types.
Code311FieldNames = """
        co_argcount
        co_posonlyargcount
        co_kwonlyargcount
        co_nlocals
        co_stacksize
        co_flags
        co_consts
        co_code
        co_names
        co_varnames
        co_freevars
        co_cellvars
        co_filename
        co_name
        co_qualname
        co_firstlineno
        co_lnotab
        co_exceptiontable
"""

Code311FieldTypes = deepcopy(Code38FieldTypes)
Code311FieldTypes.update({"co_qualname": str, "co_exceptiontable": str})


class Code311(Code38):
    """Class for a Python 3.11+ code object used when a Python interpreter less than 3.11 is
    working on Python 3.11 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.

    When done mutating, call method to_native().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise, the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.
    """

    def __init__(
        self,
        co_argcount,
        co_posonlyargcount,
        co_kwonlyargcount,
        co_nlocals,
        co_stacksize,
        co_flags,
        co_consts,
        co_code,
        co_names,
        co_varnames,
        co_freevars,
        co_cellvars,
        co_filename,
        co_name,
        co_qualname,
        co_firstlineno,
        co_linetable,
        co_exceptiontable,
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super(Code311, self).__init__(
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
            co_firstlineno=co_firstlineno,
            co_lnotab=co_linetable,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
        )
        self.co_qualname = co_qualname
        self.co_exceptiontable = co_exceptiontable
        self.fieldtypes = Code311FieldTypes
        if type(self) == Code311:
            self.check()

    def to_native(self):
        if not (PYTHON_VERSION_TRIPLE >= (3, 11)):
            raise TypeError(
                "Python Interpreter needs to be in 3.11 or greater; is %s"
                % version_tuple_to_str()
            )

        code = deepcopy(self)
        code.freeze()
        try:
            code.check()
        except AssertionError(e):
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
            code.co_qualname,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_exceptiontable,
            code.co_freevars,
            code.co_cellvars,
        )
