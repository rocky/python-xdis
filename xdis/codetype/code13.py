# (C) Copyright 2020-2021 by Rocky Bernstein
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

from xdis.codetype.base import CodeBase
from copy import deepcopy

# A Python 2 class for bytes
class Bytes(str):
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "b%s" % repr(self.s)

# If there is a list of types, then any will work, but the 1st one is the corect one for types.CodeType
Code13FieldTypes = {
    "co_argcount": int,
    "co_nlocals": int,
    "co_flags": int,
    "co_code": (str, list, tuple),
    "co_consts": (tuple, list, Bytes),
    "co_names": (tuple, list),
    "co_varnames": (tuple, list),
    "co_filename": (str, unicode, Bytes),
    "co_name": (str, unicode, Bytes),
}

class Code13(CodeBase):
    """Class for a Python 1.0 .. 1.4 code object used for Python interpreters other than 1.0 .. 1.4

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise the line number table `co_lnotab`
    can be stored as a simple list of offset, line_number tuples.
    """

    def __init__(
        self,
        co_argcount,
        co_nlocals,
        co_flags,
        co_code,
        co_consts,
        co_names,
        co_varnames,
        co_filename,
        co_name,
    ):
        self.co_argcount = co_argcount
        self.co_nlocals = co_nlocals
        self.co_flags = co_flags
        self.co_code = co_code
        self.co_consts = co_consts
        self.co_names = co_names
        self.co_varnames = co_varnames
        self.co_filename = co_filename
        self.co_name = co_name
        self.fieldtypes = Code13FieldTypes
        if type(self) == Code13:
            self.check()
        return

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

    # FIXME: use self.fieldtype
    def freeze(self):
        for field in "co_consts co_names co_varnames".split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))
        return self

    def replace(self, **kwargs):
        """
        Return a copy of the code object with new values for the specified fields.

        This is analoguous to the method added to types.CodeType in Python 3.8.
        """
        code = deepcopy(self)
        for field, value in kwargs.items():
            if not hasattr(self, field):
                raise TypeError(
                    "Code object %s doesn't have field %s" % (type(self), self)
                )
            setattr(code, field, value)
        return code
