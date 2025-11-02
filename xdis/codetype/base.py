# (C) Copyright 2020, 2024-2025 by Rocky Bernstein
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

import inspect


def iscode(obj):
    """A replacement for inspect.iscode() which we can't be used because we may be
    using a different version of Python than the version of Python used
    in creating the byte-compiled objects. Here, the code types may mismatch.
    """
    return inspect.iscode(obj) or isinstance(obj, CodeBase)


def code_has_star_arg(code):
    """Return True iff
    the code object has a variable positional parameter (*args-like)"""
    return (code.co_flags & 4) != 0


def code_has_star_star_arg(code):
    """
    Return True iff the code object has a variable keyword parameter (**kwargs-like)."""
    return (code.co_flags & 8) != 0


class CodeBase:
    # These mimic some of the attributes in a Python code type
    # co_argcount: int
    # co_consts: tuple
    # co_filename: str
    # co_firstlineno: int
    # co_kwposonlyargcount: int
    # co_name: str
    # co_nlocals: int
    # co_posonlyargcount: int
    # co_stacksize: int
    # co_varnames: tuple

    # Mimic Python 3 code access functions
    def __len__(self) -> int:
        return len(self.co_code)

    def __getitem__(self, i) -> int:
        op = self.co_code[i]
        if isinstance(op, str):
            op = ord(op)
        return op

    def __repr__(self) -> str:
        msg = (
            "<%s code object %s" % (self.__class__.__name__, self.co_name)
        ) + " at %s, file %s>" % (hex(id(self)), self.co_filename)

        if hasattr(self, "co_firstlineno"):
            msg += ", line %s" % self.co_firstlineno

        return msg
