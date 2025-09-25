# (C) Copyright 2020-2021, 2023, 2025 by Rocky Bernstein
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
from types import CodeType

from xdis.codetype.code20 import Code2, Code2FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE

# Below, in the Python 2.4 branch "bytes" is "str" since there may not be a "bytes" type.
Code3FieldTypes = deepcopy(Code2FieldTypes)
Code3FieldTypes.update(
    {
        "co_kwonlyargcount": int,
    }
)


class Code3(Code2):
    """
    Class for a Python3 code object used when a Python not in the
    range between 3.0 and 3.7 but is working on Python 3.0 ... 3.7
    bytecode. It also functions as an object that can be used to
    build or write a Python3 code object, since we allow mutable
    structures.  When done mutating, call method freeze().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise, the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.
    """

    def __init__(
        self,
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
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super(Code3, self).__init__(
            co_argcount=co_argcount,
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
        self.co_kwonlyargcount = co_kwonlyargcount
        self.fieldtypes = Code3FieldTypes

        if type(self) == Code3:
            self.check()
        return

    def encode_lineno_tab(self):
        co_lnotab = ""

        prev_line_number = self.co_firstlineno
        prev_offset = 0
        for offset, line_number in self.co_lnotab:
            offset_diff = offset - prev_offset
            line_diff = line_number - prev_line_number
            prev_offset = offset
            prev_line_number = line_number
            while offset_diff >= 256:
                co_lnotab += bytearray([255, 0])
                offset_diff -= 255
            while line_diff >= 256:
                co_lnotab += bytearray([0, 255])
                line_diff -= 255
            if 0 <= line_diff <= 256:
                # FIXME: should warn about dropping off a line number
                co_lnotab += bytearray([offset_diff, line_diff])

        self.co_lnotab = co_lnotab

    def freeze(self):
        for field in "co_consts co_names co_varnames co_freevars co_cellvars".split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))

        # for field, typename in self.fieldtypes:
        #     pass

        if isinstance(self.co_lnotab, dict):
            d = self.co_lnotab
            self.co_lnotab = sorted(zip(d.keys(), d.values()), key=lambda tup: tup[0])
        if isinstance(self.co_lnotab, list):
            # We assume we have a list of tuples:
            # (offset, linenumber) which we convert
            # into the encoded format
            self.encode_lineno_tab()

        if isinstance(self.co_lnotab, str):
            self.co_lnotab = self.co_lnotab.encode()

        return self

    def to_native(self):
        if not (3, 0) <= PYTHON_VERSION_TRIPLE < (3, 8):
            raise TypeError(
                "Python Interpreter needs to be in range 3.0..3.7; is %s"
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
