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

import inspect


def iscode(obj):
    """A replacement for inspect.iscode() which we can't used because we may be
    using a different version of Python than the version of Python used
    in creating the byte-compiled objects. Here, the code types may mismatch.
    """
    return inspect.iscode(obj) or isinstance(obj, CodeBase)


def code_has_star_arg(code):
    """Return True iff
    the code object has a variable positional parameter (*args-like)"""
    return (code.co_flags & 4) != 0


def code_has_star_star_arg(code):
    """Return True iff
    The code object has a variable keyword parameter (**kwargs-like)."""
    return (code.co_flags & 8) != 0


class CodeBase(object):

    # Mimic Python 3 code access functions
    def __len__(self):
        return len(self.co_code)

    def __getitem__(self, i):
        op = self.co_code[i]
        if isinstance(op, str):
            op = ord(op)
        return op

    def __repr__(self):
        msg = "<%s code object %s at 0x%x, file %s>" % (
            (self.__class__.__name__, self.co_name, id(self), self.co_filename)
        )
        if hasattr(self, "co_firstlineno"):
            msg += ", line %d" % self.co_firstlineno

        return msg
