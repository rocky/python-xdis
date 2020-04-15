# (C) Copyright 2017-2020 by Rocky Bernstein
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

from xdis.version_info import PYTHON3, PYTHON_VERSION
from xdis.codetype.code30 import Code3
import types
from copy import deepcopy

# Note: order is the positional order. It is important to match this
# with the 3.8 order.
Code3FieldNames = """
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

Code38FieldTypes = {
    "co_argcount": int,
    "co_posonlyargcount": int,
    "co_kwonlyargcount": int,
    "co_nlocals": int,
    "co_stacksize": int,
    "co_flags": int,
    "co_code": bytes,
    "co_consts": tuple,
    "co_names": tuple,
    "co_varnames": tuple,
    "co_filename": str,
    "co_name": str,
    "co_firstlineno": int,
    "co_lnotab": bytes,
    "co_freevars": tuple,
    "co_cellvars": tuple,
}
# posonlyargcount field added to 3.0 .. 3.7 field


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

    def check(self, opts={}):
        for (
            field
        ) in "co_argcount co_posonlyargcount co_kwonlyargcount co_nlocals co_flags co_firstlineno".split():
            val = getattr(self, field)
            assert isinstance(val, int), "%s should be int, is %s" % (field, type(val))
        for field in "co_consts co_names co_varnames".split():
            val = getattr(self, field)
            assert isinstance(val, tuple), "%s should be tuple, is %s" % (
                field,
                type(val),
            )

    def to_native(self):
        if not (PYTHON_VERSION >= 3.8):
            raise TypeError(
                "Python Interpreter needs to be in 3.8 or greater; is %s"
                % PYTHON_VERSION
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
            code.co_lnotab,
            code.co_freevars,
            code.co_cellvars,
        )
