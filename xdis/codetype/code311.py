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

# Note: order is the positional order. It is important to match this
# with the 3.11 order.
Code311FieldNames = """
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
        co_filename
        co_name
        co_qualname
        co_firstlineno
        co_lnotab
        co_exception_table
        co_freevars
        co_cellvars
"""

Code311FieldTypes = deepcopy(Code38FieldTypes)
Code311FieldTypes.update({"co_qualname": str, "co_exception_table": bytes})


class Code311(Code38):
    """Class for a Python 3.11+ code object used when a Python interpreter less than 3.11 is
    working on Python3 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.

    When done mutating, call method to_native().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise the line number table `co_lnotab`
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
        co_code,
        co_consts,
        co_names,
        co_varnames,
        co_filename,
        co_name,
        co_qualname,
        co_firstlineno,
        co_lnotab,
        co_exception_table,
        co_freevars,
        co_cellvars,
    ):
        super(Code311, self).__init__(
            co_argcount,
            co_posonlyargcount,
            co_kwonlyargcount,
            co_nlocals,
            co_stacksize,
            co_flags,
            co_code,
            co_consts,
            co_names,
            co_qualname,
            co_varnames,
            co_filename,
            co_name,
            co_firstlineno,
            co_lnotab,
            co_exceptiontable,
            co_freevars,
            co_cellvars,
        )
        self.co_qualname = co_qualname
        self.co_exception_table = co_exception_table
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
            code.co_qualname,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_exception_table,
            code.co_freevars,
            code.co_cellvars,
        )
