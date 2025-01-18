# (C) Copyright 2020-2021, 2023-2024 by Rocky Bernstein
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
from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

from xdis.codetype.code310 import Code310, Code310FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str


# Note: order is the positional order given in the Python docs for
# 3.11 types.Codetype.
# "posonlyargcount" is not used, but it is in other Python versions, so it
# has to be included since this structure is used as the Union type
# for all code types.
Code311FieldNames = """
        co_argcount
        co_posonlyargcount
        co_kwonlyargcount
        co_nlocals
        co_stacksize
        co_flags
        co_consts
        co_code
        co_names
        co_varnames
        co_freevars
        co_cellvars
        co_filename
        co_name
        co_qualname
        co_firstlineno
        co_linetable
        co_exceptiontable
"""

Code311FieldTypes = deepcopy(Code310FieldTypes)
Code311FieldTypes.update({"co_qualname": str, "co_exceptiontable": bytes})


##### Parse location table #####
def parse_location_entries(location_bytes, first_line):
    """
    Parses the locations table described in: https://github.com/python/cpython/blob/3.11/Objects/locations.md
    The locations table replaced the line number table starting in 3.11
    """

    def starts_new_entry(b):
        return bool(b & 0b10000000)  # bit 7 is set

    def extract_code(b):
        return (b & 0b01111000) >> 3  # extracts bits 3-6

    def extract_length(b):
        return (b & 0b00000111) + 1  # extracts bit 0-2

    def iter_location_codes(loc_bytes):
        if len(loc_bytes) == 0:
            return []

        iter_locs = iter(loc_bytes)
        entry_codes = [next(iter_locs)]

        for b in iter_locs:
            if starts_new_entry(b):
                yield entry_codes
                entry_codes = [b]
            else:
                entry_codes.append(b)

        if entry_codes:
            yield entry_codes

    def iter_varints(varint_bytes):
        if len(varint_bytes) == 0:
            return []

        def has_next_byte(b):
            return bool(b & 0b0100_0000)  # has bit 6 set

        def get_value(b):
            return b & 0b00111111  # extracts bits 0-5

        iter_varint_bytes = iter(varint_bytes)

        current_value = 0
        shift_amt = 0

        for b in iter_varint_bytes:
            current_value += get_value(b) << shift_amt
            if has_next_byte(b):
                shift_amt += 6
            else:
                yield current_value
                current_value = 0
                shift_amt = 0

    def decode_signed_varint(s):
        return -(s >> 1) if s & 1 else (s >> 1)

    entries = (
        []
    )  # tuples of (code units, start line, end line, start column, end column)

    last_line = first_line

    for location_codes in iter_location_codes(location_bytes):
        first_byte = location_codes[0]
        location_length = extract_length(first_byte)
        code = extract_code(first_byte)

        if code <= 9:  # short form
            start_line = last_line
            end_line = start_line
            second_byte = location_codes[1]
            start_column = (code * 8) + ((second_byte >> 4) & 7)
            end_column = start_column + (second_byte & 15)
        elif code <= 12:  # one line form
            start_line = last_line + code - 10
            end_line = start_line
            start_column = location_codes[1]
            end_column = location_codes[2]
        elif code == 13:  # no column info
            (start_line_delta,) = iter_varints(location_codes[1:])
            start_line = last_line + decode_signed_varint(start_line_delta)
            end_line = start_line
            start_column = None
            end_column = None
        elif code == 14:  # long form
            (start_line_delta, end_line_delta, start_column, end_column) = iter_varints(
                location_codes[1:]
            )
            start_line = last_line + decode_signed_varint(start_line_delta)
            end_line = start_line + end_line_delta
        else:  # code == 15, no location
            start_line = None
            end_line = None
            start_column = None
            end_column = None

        entries.append(
            (location_length, start_line, end_line, start_column, end_column)
        )

        last_line = start_line if start_line is not None else last_line

    return entries


##### NEW "OPAQUE" LINE TABLE PARSING #####
# See: https://github.com/python/cpython/blob/aaed91cabcedc16c089c4b1c9abb1114659a83d3/Objects/codeobject.c#L1245C1-L1245C17
PY_CODE_LOCATION_INFO_SHORT0 = 0
PY_CODE_LOCATION_INFO_ONE_LINE0 = 10
PY_CODE_LOCATION_INFO_ONE_LINE1 = 11
PY_CODE_LOCATION_INFO_ONE_LINE2 = 12

PY_CODE_LOCATION_INFO_NO_COLUMNS = 13
PY_CODE_LOCATION_INFO_LONG = 14
PY_CODE_LOCATION_INFO_NONE = 15


@dataclass(frozen=True)
class LineTableEntry:
    line_delta: int
    code_delta: int
    no_line_flag: bool


def _scan_varint(remaining_linetable: Iterable[int]) -> int:
    value = 0
    for shift, read in enumerate(remaining_linetable):
        value |= (read & 63) << (shift * 6)
        if not (read & 64):
            break
    return value


def _scan_signed_varint(remaining_linetable: Iterable[int]) -> int:
    value = _scan_varint(remaining_linetable)
    if value & 1:
        return -(value >> 1)
    return value >> 1


def _get_line_delta(code_byte: int, remaining_linetable: Iterable[int]):
    line_delta_code = (code_byte >> 3) & 15
    if line_delta_code == PY_CODE_LOCATION_INFO_NONE:
        return 0
    if line_delta_code in (
        PY_CODE_LOCATION_INFO_NO_COLUMNS,
        PY_CODE_LOCATION_INFO_LONG,
    ):
        return _scan_signed_varint(remaining_linetable)
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE0:
        return 0
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE1:
        return 1
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE2:
        return 2
    return 0


def _is_no_line_marker(linetable_code_byte: int):
    return (linetable_code_byte >> 3) == 0x1F


def _next_code_delta(linetable_code_byte: int):
    return ((linetable_code_byte & 7) + 1) * 2


def _test_check_bit(linetable_code_byte: int):
    return bool(linetable_code_byte & 128)


def _go_to_next_code_byte(remaining_linetable: Iterator[int]) -> Optional[int]:
    try:
        while not _test_check_bit((code_byte := next(remaining_linetable))):
            pass
    except StopIteration:
        return None
    return code_byte


def decode_linetable_entry(
    code_byte: int, remaining_linetable: Iterable[int]
) -> LineTableEntry:
    assert _test_check_bit(code_byte), "malformed linetable"
    return LineTableEntry(
        line_delta=_get_line_delta(
            code_byte=code_byte, remaining_linetable=remaining_linetable
        ),
        code_delta=_next_code_delta(linetable_code_byte=code_byte),
        no_line_flag=_is_no_line_marker(linetable_code_byte=code_byte),
    )


def parse_linetable(linetable: bytes, first_lineno: int):

    linetable_entries: list[LineTableEntry] = []

    # decode linetable entries
    iter_linetable = iter(linetable)
    while (code_byte := _go_to_next_code_byte(iter_linetable)) is not None:
        linetable_entries.append(
            decode_linetable_entry(
                code_byte=code_byte, remaining_linetable=iter_linetable
            )
        )

    if not linetable_entries:
        return

    first_entry, *remaining_entries = linetable_entries

    # compute co_lines()
    code_start: int = 0
    code_end: int = first_entry.code_delta
    line: int = first_lineno + first_entry.line_delta
    no_line_flag = first_entry.no_line_flag
    for linetable_entry in remaining_entries:
        if (
            linetable_entry.line_delta != 0
            or linetable_entry.no_line_flag != no_line_flag
        ):
            # if the line changes, emit the current entry
            yield (code_start, code_end, None if no_line_flag else line)

            line += linetable_entry.line_delta
            no_line_flag = linetable_entry.no_line_flag
            code_start = code_end
        code_end += linetable_entry.code_delta

    yield (code_start, code_end, None if no_line_flag else line)


@dataclass(frozen=True)
class PositionEntry:
    line_delta: int
    num_lines: int
    code_delta: int
    column: int
    endcolumn: int
    no_line_flag: bool


def decode_position_entry(
    code_byte: int, remaining_linetable: Iterator[int]
) -> PositionEntry:
    assert _test_check_bit(code_byte), "malformed linetable"

    code_delta = _next_code_delta(code_byte)

    no_line_flag = False
    column = -1
    endcolumn = -1
    line_delta = 0
    num_lines = 0

    location_flags = (code_byte >> 3) & 15
    if location_flags == PY_CODE_LOCATION_INFO_NONE:
        no_line_flag = True
    elif location_flags == PY_CODE_LOCATION_INFO_LONG:
        line_delta = _scan_signed_varint(remaining_linetable)
        num_lines = _scan_varint(remaining_linetable)
        column = _scan_varint(remaining_linetable) - 1
        endcolumn = _scan_varint(remaining_linetable) - 1
    elif location_flags == PY_CODE_LOCATION_INFO_NO_COLUMNS:
        line_delta = _scan_signed_varint(remaining_linetable)
    elif location_flags in (
        PY_CODE_LOCATION_INFO_ONE_LINE0,
        PY_CODE_LOCATION_INFO_ONE_LINE1,
        PY_CODE_LOCATION_INFO_ONE_LINE2,
    ):
        line_delta = location_flags - 10
        column = next(remaining_linetable)
        endcolumn = next(remaining_linetable)
    else:
        second_byte = next(remaining_linetable)
        assert not _test_check_bit(second_byte)
        column = (location_flags << 3) | (second_byte >> 4)
        endcolumn = column + (second_byte & 15)

    return PositionEntry(
        line_delta=line_delta,
        num_lines=num_lines,
        code_delta=code_delta,
        column=column,
        endcolumn=endcolumn,
        no_line_flag=no_line_flag,
    )


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


class Code311(Code310):
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
    ):
        # Keyword argument parameters in the call below is more robust.
        # Since things change around, robustness is good.
        super(Code311, self).__init__(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=co_kwonlyargcount,
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
            co_linetable=co_linetable,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
        )
        self.co_qualname = co_qualname
        self.co_exceptiontable = co_exceptiontable
        self.fieldtypes = Code311FieldTypes
        if type(self) == Code311:
            self.check()

    def to_native(self):
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
