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

from xdis.version_info import PYTHON_VERSION
from xdis.codetype.code30 import Code3, Code3FieldTypes
import types
from copy import deepcopy

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
        co_filename
        co_name
        co_firstlineno
        co_lnotab
        co_freevars
        co_cellvars
"""

Code38FieldTypes = deepcopy(Code3FieldTypes)
Code38FieldTypes.update({
    "co_posonlyargcount": int,
})



class Code38(Code3):
    """Class for a Python 3.8+ code object used when a Python interpreter less than 3.8 is
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
        co_firstlineno,
        co_lnotab,
        co_freevars,
        co_cellvars,
    ):
        super(Code38, self).__init__(
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
            co_cellvars,
        )
        self.co_posonlyargcount = co_posonlyargcount
        self.fieldtypes = Code38FieldTypes
        if type(self) == Code38:
            self.check()

    def to_native(self):
        raise TypeError(
            "Python Interpreter needs to be in 3.8 or greater; is %s"
            % ".".join([str(v) for v in PYTHON_VERSION_TRIPLE])
        )
