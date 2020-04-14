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
from xdis.codetype.base import CodeBase
import inspect, types

Code13Fields = tuple("""
        co_argcount
        co_nlocals
        co_flags
        co_code
        co_consts
        co_names
        co_varnames
        co_filename
        co_name
""".split())

class Code13(CodeBase):
    """Class for a Python 1.3 .. 1.5 code object used for Python interpreters other than 1.3 .. 1.5

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
        return

    def freeze(self):
        for field in "co_consts co_names co_varnames".split():
            val = getattr(self, field)
            if isinstance(val, list):
                setattr(self, field, tuple(val))
        return self

    def check(self):
        for field in "co_argcount co_nlocals co_flags".split():
            val = getattr(self, field)
            assert isinstance(val, int), "%s should be int, is %s" % (field, type(val))
        for field in "co_consts co_names co_varnames".split():
            val = getattr(self, field)
            assert isinstance(val, tuple), "%s should be tuple, is %s" % (
                field,
                type(val),
            )
