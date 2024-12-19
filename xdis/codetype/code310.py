# (C) Copyright 2024 by Rocky Bernstein
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

import struct

from xdis.codetype.code38 import Code38
from xdis.cross_types import UnicodeForPython3
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

# Note: order is the positional order. It is important to match this
# with the 3.8 order.
Code310FieldNames = """
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
        co_linetable
"""

Code310FieldTypes = {
    "co_argcount": int,
    "co_nlocals": int,
    "co_flags": int,
    "co_code": (bytes, list, str),
    "co_consts": (tuple, list),
    "co_names": (tuple, list),
    "co_varnames": (tuple, list),
    "co_filename": (str, bytes, UnicodeForPython3),
    "co_name": (str, bytes, UnicodeForPython3),
    "co_stacksize": int,
    "co_firstlineno": int,
    "co_linetable": (str, bytes, dict),
    "co_freevars": (tuple, list),
    "co_cellvars": (tuple, list),
    "co_kwonlyargcount": int,
    "co_posonlyargcount": int,
}


class Code310(Code38):
    """Class for a Python 3.10 code object used when a Python
    interpreter is not 3.10 but working on Python 3.10 bytecode. It
    also functions as an object that can be used to build or write a
    Python3 code object, since we allow mutable structures.

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
        co_filename: str,
        co_name: str,
        co_firstlineno: int,
        co_linetable,
        co_freevars,
        co_cellvars,
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        self.co_argcount = co_argcount
        self.co_kwonlyargcount = co_kwonlyargcount
        self.co_nlocals = co_nlocals
        self.co_stacksize = co_stacksize
        self.co_flags = co_flags
        self.co_code = co_code
        self.co_consts = co_consts
        self.co_names = co_names
        self.co_varnames = co_varnames
        self.co_filename = co_filename
        self.co_name = co_name
        self.co_firstlineno = co_firstlineno
        self.co_linetable = co_linetable
        self.co_freevars = co_freevars
        self.co_cellvars = co_cellvars
        self.co_posonlyargcount = co_posonlyargcount
        self.fieldtypes = Code310FieldTypes
        if type(self) == Code310:
            self.check()

    def check(self):
        for field, fieldtype in self.fieldtypes.items():
            val = getattr(self, field)
            if isinstance(fieldtype, tuple):
                assert (
                    type(val) in fieldtype
                ), "%s should be one of the types %s; is type %s" % (
                    field,
                    fieldtype,
                    type(val),
                )
            else:
                assert isinstance(
                    val, fieldtype
                ), "%s should have type %s; is type %s" % (field, fieldtype, type(val))
                pass
            pass

    def co_lines(self):
        """
        From https://peps.python.org/pep-0626/#the-new-co-lines-method-of-code-objects:

        The co_lines() returns an iterator which yields tuples of
        values, each representing the line number of a range of
        bytecodes. Each tuple will consist of three values:

        start – The offset (inclusive) of the start of the bytecode
        range end – The offset (exclusive) of the end of the bytecode
        range line – The line number, or None if the bytecodes in the
                     given range do not have a line number.  The sequence generated
                     has the following properties:

                     The first range in the sequence with have a start
                     of 0 The (start, end) ranges will be
                     non-decreasing and consecutive. That is, for any
                     pair of tuples the start of the second will equal
                     to the end of the first.  No range will be
                     backwards, that is end >= start for all triples.
                     The final range in the sequence with have end
                     equal to the size of the bytecode.  line will
                     either be a positive integer, or None

        Parsing implementation adapted from: https://github.com/python/cpython/blob/3.10/Objects/lnotab_notes.txt
        """
        line = self.co_firstlineno
        end_offset = 0
        # co_linetable is pairs of (offset_delta: unsigned byte, line_delta: signed byte)
        for offset_delta, line_delta in struct.iter_unpack('=Bb', self.co_linetable):
            assert isinstance(line_delta, int)
            assert isinstance(offset_delta, int)
            if line_delta == 0: # No change to line number, just accumulate changes to end
                end_offset += offset_delta
                continue
            start_offset = end_offset
            end_offset = start_offset + offset_delta
            if line_delta == -128: # No valid line number -- skip entry
                continue
            line += line_delta
            if end_offset == start_offset: # Empty range, omit.
                continue
            yield start_offset, end_offset, line

    def encode_lineno_tab(self):
        """
        Convert a list of (offset, line_number) encoding of
        co_linetable into the compacted 3.10-encoded format described
        in lnotab_notes.txt.

        """
        co_linetable = b""

        prev_line_number = self.co_firstlineno
        prev_offset = 0
        offset_diff = 0

        for offset, line_number in self.co_linetable:
            line_diff = line_number - prev_line_number
            prev_line_number = line_number
            offset_diff = offset - prev_offset
            prev_offset = offset
            while offset_diff >= 256:
                co_linetable += bytearray([255, 0])
                offset_diff -= 255
            co_linetable += bytearray([offset_diff, line_diff % 256])
            while line_diff >= 127:
                co_linetable += bytearray([0, 127])
                line_diff -= 127
            while line_diff < -127:
                co_linetable += bytearray([0, -127])
                line_diff -= 127

        self.co_linetable = co_linetable

    def freeze(self):
        for field in "co_consts co_names co_varnames co_freevars co_cellvars".split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))

        # for field, typename in self.fieldtypes:
        #     pass

        if isinstance(self.co_linetable, dict):
            d = self.co_linetable
            self.co_linetable = sorted(
                zip(d.keys(), d.values()), key=lambda tup: tup[0]
            )

        if isinstance(self.co_linetable, list):
            # We assume we have a list of tuples:
            # (offset, linenumber) which we convert
            # into the encoded format
            self.encode_lineno_tab()

        if isinstance(self.co_code, str) and PYTHON_VERSION_TRIPLE >= (3, 0):
            self.co_code = self.co_code.encode()

        if isinstance(self.co_linetable, str):
            self.co_linetable = self.co_linetable.encode()

        return self

    def to_native(self) -> types.CodeType:
        if (3, 10) != PYTHON_VERSION_TRIPLE[:2]:
            raise TypeError(
                f"Python Interpreter needs to be 3.10; is {version_tuple_to_str()}"
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
            code.co_linetable,
            code.co_freevars,
            code.co_cellvars,
        )
