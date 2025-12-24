# (C) Copyright 2025 by Rocky Bernstein
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

from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from xdis.codetype.code311 import Code311


@dataclass
class SourceLocation:
    # 1-based integer line number
    line_number: int
    # column offset in line: 1-based int (constructed from a zero-indexed stored value)
    column_offset: int


class Code313Rust(Code311):
    """Class for a RustPython 3.13 code object used when a Python
    interpreter is not RustPython 3.13 but working on RustPython 3.13 bytecode. It
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
        co_flags: int,
        co_code: bytes,
        co_consts: tuple,
        co_names: tuple[str],
        co_varnames: tuple[str],
        co_filename: str,
        co_name: str,
        co_qualname: str,
        co_firstlineno: int,
        co_linetable: bytes,
        co_freevars: tuple,
        co_cellvars: tuple,
        version_triple: Tuple[int, int, int],
        locations: tuple,
        co_exceptiontable = tuple(),
        collection_order: Dict[Union[set, frozenset, dict], Tuple[Any]] = {},
    ) -> None:
        self.co_argcount = co_argcount
        self.co_posonlyargcount = co_posonlyargcount
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
        self.co_firstlineno = co_firstlineno    # None if 0 in serialized form
        self.co_linetable = co_linetable
        self.co_qualname = co_qualname
        self.co_cellvars = co_cellvars
        self.co_linetable = co_linetable
        self.co_freevars= co_freevars
        self.co_exceptiontable = co_exceptiontable
        self.co_collection_order = collection_order
        self.version_triple = version_triple
        self.locations = locations
