# (C) Copyright 2020-2021, 2023-2025 by Rocky Bernstein
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
from typing import Any, Dict, Set, Tuple

from xdis.codetype.code311 import (
    Code311,
    Code311FieldTypes,
    PositionEntry,
    decode_position_entry,
    parse_linetable,
    parse_location_entries,
)
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

# Note: order is the positional order given in the Python docs for
# 3.11 types.Codetype.
# "posonlyargcount" is not used, but it is in other Python versions, so it
# has to be included since this structure is used as the Union type
# for all code types.
Code311GraalFieldNames = """
        co_argcount
        co_cellvars
        co_code
        co_consts
        co_exceptiontable
        co_filename
        co_firstlineno
        co_flags
        co_freevars
        co_kwonlyargcount
        co_lines
        co_lnotab
        co_name
        co_names
        co_nlocals
        co_posonlyargcount
        co_qualname
        co_stacksize
        co_varnames
        condition_profileCount
        endColumn
        endLine
        exception_handler_ranges
        generalizeInputsMap
        generalizeVarsMap
        outputCanQuicken
        primitiveConstants
        srcOffsetTable
        startColumn
        startLine
        variableShouldUnbox
"""

Code311GraalFieldTypes = deepcopy(Code311FieldTypes)
Code311GraalFieldTypes.update({"co_qualname": str, "co_exceptiontable": bytes})


def parse_positions(linetable: bytes, first_lineno: int):
    position_entries: list[PositionEntry] = []

    # decode linetable entries
    iter_linetable = iter(linetable)
    try:
        while (code_byte := next(iter_linetable)) is not None:
            position_entries.append(
                decode_position_entry(
                    code_byte=code_byte, remaining_linetable=iter_linetable
                )
            )
    except StopIteration:
        pass

    computed_line = first_lineno
    for position_entry in position_entries:
        computed_line += position_entry.line_delta
        for _ in range(0, position_entry.code_delta, 2):
            if position_entry.no_line_flag:
                yield (None, None, None, None)
            else:
                yield (
                    computed_line,
                    computed_line + position_entry.num_lines,
                    position_entry.column,
                    position_entry.endcolumn,
                )


class Code311Graal(Code311):
    """Class for a Python 3.11+ code object used when a Python interpreter less than 3.11 is
    working on Python 3.11 bytecode. It also functions as an object that can be used
    to build or write a Python3 code object, since we allow mutable structures.

    When done mutating, call method to_native().

    For convenience in generating code objects, fields like
    `co_consts`, co_names which are (immutable) tuples in the end-result can be stored
    instead as (mutable) lists. Likewise, the line number table `co_linetable`
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
        co_consts,
        co_code,
        co_names,
        co_varnames,
        co_freevars,
        co_cellvars,
        co_filename,
        co_name,
        co_qualname,
        co_firstlineno,
        co_linetable,
        co_exceptiontable,
        reference_objects: Set[Any] = set(),
        version_triple: Tuple[int, int, int] = (0, 0, 0),
        other_fields: Dict[str, Any] = {},
    ) -> None:
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super().__init__(
            co_argcount=co_argcount,
            co_cellvars=co_cellvars,
            co_code=co_code,
            co_consts=co_consts,
            co_exceptiontable=co_exceptiontable,
            co_filename=co_filename,
            co_firstlineno=co_firstlineno,
            co_flags=co_flags,
            co_freevars=co_freevars,
            co_kwonlyargcount=co_kwonlyargcount,
            co_linetable=co_linetable,
            co_name=co_name,
            co_names=co_names,
            co_nlocals=co_nlocals,
            co_qualname=co_qualname,
            co_posonlyargcount=co_posonlyargcount,
            co_stacksize=co_stacksize,
            co_varnames=co_varnames,
            reference_objects=reference_objects,
            version_triple=version_triple,
        )

        for field_name, value in other_fields.items():
            setattr(self, field_name, value)

        self.co_qualname = co_qualname
        self.co_exceptiontable = co_exceptiontable
        self.fieldtypes = Code311GraalFieldTypes
        if type(self) is Code311Graal:
            self.check()

    def to_native(self) -> CodeType:
        if not (PYTHON_VERSION_TRIPLE >= (3, 11)):
            raise TypeError(
                "Python Interpreter needs to be in 3.11 or greater; is %s"
                % version_tuple_to_str()
            )

        code = deepcopy(self)
        code.freeze()
        try:
            code.check()
        except AssertionError as e:
            raise TypeError(e)

        if code.co_exceptiontable is None:
            code.co_exceptiontable = b""
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
            code.co_qualname,
            code.co_firstlineno,
            code.co_linetable,
            code.co_exceptiontable,
            code.co_freevars,
            code.co_cellvars,
        )

    def co_lines(self):
        return parse_linetable(self.co_linetable, self.co_firstlineno)

    def co_positions(self):
        return parse_location_entries(self.co_linetable, self.co_firstlineno)
