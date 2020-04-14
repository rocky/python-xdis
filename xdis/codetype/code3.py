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

from xdis.codetype.code2 import Code2
from xdis.version_info import PYTHON3, PYTHON_VERSION
import types


Code3Fields = tuple("""
        co_argcount
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
""".split())
# Field co_kwonlyargcount is new. The datatypes of some fields may be different.

class Code3(Code2):
    """Class for a Python3 code object used when a Python interpreter less than 3 is
    working on Python3 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.
    When done mutating, call method freeze().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise the line number table `co_lnotab`
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
        super(Code3, self).__init__(
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
            co_firstlineno,
            co_lnotab,
            co_freevars,
            co_cellvars,
        )
        self.co_kwonlyargcount = co_kwonlyargcount

    def encode_lineno_tab(self):
        co_lnotab = b""

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
            co_lnotab += bytearray([offset_diff, line_diff])

        self.co_lnotab = co_lnotab

    def freeze(self):
        for field in "co_consts co_names co_varnames co_freevars co_cellvars".split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))

        if isinstance(self.co_lnotab, dict):
            d = self.co_lnotab
            self.co_lnotab = sorted(zip(d.keys(), d.values()), key=lambda tup: tup[0])
        if isinstance(self.co_lnotab, list):
            # We assume we have a list of tuples:
            # (offset, linenumber) which we convert
            # into the encoded format
            self.encode_lineno_tab()

        return self

    def check(self, opts={}):
        for (
            field
        ) in (
            "co_argcount co_kwonlyargcount, co_nlocals co_flags co_firstlineno".split()
        ):
            val = getattr(self, field)
            assert isinstance(val, int), "%s should be int, is %s" % (field, type(val))
        for field in "co_consts co_names co_varnames".split():
            val = getattr(self, field)
            assert isinstance(val, tuple), "%s should be tuple, is %s" % (
                field,
                type(val),
            )

    def to_native(self):
        if not (3.0 <= PYTHON_VERSION <= 3.7):
            raise TypeError(
                "Python Interpreter needs to be in range 3.0..3.7; is %s"
                % PYTHON_VERSION
            )

        try:
            self.check()
        except AssertionError as e:
            raise TypeError(e)

        return types.Code(
            self.co_nlocals,
            self.co_stacksize,
            self.co_flags,
            self.co_code,
            self.co_consts,
            self.co_names,
            self.co_varnames,
            self.co_filename,
            self.co_name,
            self.co_firstlineno,
            self.co_lnotab,
            self.co_freevars,
            self.co_cellvars,
        )


class Code3Compat(Code3):
    """A much more flexible version of Code. We don't require
    kwonlyargcount which does't exist in Python 2. You can also fill
    in what you want and leave the rest blank.  Remmeber though to
    call inherited function freeze when done.
    """

    def __init__(
        self,
        co_argcount=0,
        co_kwonlyargcount=0,
        co_nlocals=0,
        co_stacksize=0,
        co_flags=[],
        co_code=[],
        co_consts=[],
        co_names=[],
        co_varnames=[],
        co_filename="unknown",
        co_name="unknown",
        co_firstlineno=1,
        co_lnotab="",
        co_freevars=[],
        co_cellvars=[],
    ):
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
        self.co_lnotab = co_lnotab
        self.co_freevars = co_freevars
        self.co_cellvars = co_cellvars

    def __repr__(self):
        return '<code3 object %s at 0x%0x, file "%s", line %d>' % (
            self.co_name,
            id(self),
            self.co_filename,
            self.co_firstlineno,
        )


def code3compat(co):
    return Code3Compat(
        co.co_argcount,
        co.co_kwonlyargcount,
        co.co_nlocals,
        co.co_stacksize,
        co.co_flags,
        co.co_code,
        co.co_consts,
        co.co_names,
        co.co_varnames,
        co.co_filename,
        co.co_name,
        co.co_firstlineno,
        co.co_lnotab,
        co.co_freevars,
        co.co_cellvars,
    )
