import types
from copy import deepcopy

from xdis.codetype.code311 import Code311, Code311FieldTypes
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

from dataclasses import dataclass
from typing import Iterable, Iterator, Generator

Code313FieldNames = Code311FieldTypes.copy()
Code313FieldTypes = deepcopy(Code311FieldTypes)

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
    if line_delta_code in (PY_CODE_LOCATION_INFO_NO_COLUMNS, PY_CODE_LOCATION_INFO_LONG):
        return _scan_signed_varint(remaining_linetable)
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE0:
        return 0
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE1:
        return 1
    if line_delta_code == PY_CODE_LOCATION_INFO_ONE_LINE2:
        return 2
    return 0

def _is_no_line_marker(linetable_code_byte: int):
    return (linetable_code_byte >> 3) == 0x1f

def _next_code_delta(linetable_code_byte: int):
    return ((linetable_code_byte & 7) + 1) * 2

def _test_check_bit(linetable_code_byte: int):
    return bool(linetable_code_byte & 128)

def _go_to_next_code_byte(remaining_linetable: Iterator[int]) -> int:
    try:
        while not _test_check_bit((code_byte := next(remaining_linetable))):
            pass
    except StopIteration:
        return None
    return code_byte

def decode_linetable_entry(code_byte: int, remaining_linetable: Iterable[int]) -> LineTableEntry:
    assert _test_check_bit(code_byte), "malformed linetable"
    return LineTableEntry(
        line_delta=_get_line_delta(code_byte=code_byte, remaining_linetable=remaining_linetable),
        code_delta=_next_code_delta(linetable_code_byte=code_byte),
        no_line_flag=_is_no_line_marker(linetable_code_byte=code_byte)
    )

def parse_linetable(linetable: bytes, first_lineno: int):
    
    linetable_entries: list[LineTableEntry] = []
    
    # decode linetable entries
    iter_linetable = iter(linetable)
    while (code_byte := _go_to_next_code_byte(iter_linetable)) is not None:
        linetable_entries.append(decode_linetable_entry(code_byte=code_byte, remaining_linetable=iter_linetable))

    if not linetable_entries:
        return

    first_entry, *remaining_entries = linetable_entries

    # compute co_lines()
    code_start: int = 0
    code_end: int = first_entry.code_delta
    line: int = first_lineno + first_entry.line_delta
    no_line_flag = first_entry.no_line_flag
    for linetable_entry in remaining_entries:
        if linetable_entry.line_delta != 0 or linetable_entry.no_line_flag != no_line_flag:
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

def decode_position_entry(code_byte: int, remaining_linetable: Iterator[int]) -> PositionEntry:
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
    elif location_flags in (PY_CODE_LOCATION_INFO_ONE_LINE0, PY_CODE_LOCATION_INFO_ONE_LINE1, PY_CODE_LOCATION_INFO_ONE_LINE2):
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
        no_line_flag=no_line_flag
    )

def parse_positions(linetable: bytes, first_lineno: int):
    position_entries: list[PositionEntry] = []
    
    # decode linetable entries
    iter_linetable = iter(linetable)
    try:
        while (code_byte := next(iter_linetable)) is not None:
            position_entries.append(decode_position_entry(code_byte=code_byte, remaining_linetable=iter_linetable))
    except StopIteration:
        pass

    computed_line = first_lineno
    for position_entry in position_entries:
        computed_line += position_entry.line_delta
        for _ in range(0, position_entry.code_delta, 2):
            if position_entry.no_line_flag:
                yield (None, None, None, None)
            else:
                yield (computed_line, computed_line + position_entry.num_lines, position_entry.column, position_entry.endcolumn)
#####


class Code313(Code311):
    """ Class for a Python 3.13+ code object
    New CPython "undocumented" changes make this necessary to parse the co_linetable with co_lines().
    See: https://github.com/python/cpython/blob/aaed91cabcedc16c089c4b1c9abb1114659a83d3/Objects/codeobject.c#L1245C1-L1245C17
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
        super(Code313, self).__init__(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=co_kwonlyargcount,
            co_nlocals=co_nlocals,
            co_stacksize=co_stacksize,
            co_flags=co_flags,
            co_consts=co_consts,
            co_code=co_code,
            co_names=co_names,
            co_varnames=co_varnames,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_filename=co_filename,
            co_name=co_name,
            co_qualname=co_qualname,
            co_firstlineno=co_firstlineno,
            co_linetable=co_linetable,
            co_exceptiontable=co_exceptiontable,
        )
        self.fieldtypes = Code313FieldTypes
        if type(self) == Code313:
            self.check()

    def to_native(self):
        if not (PYTHON_VERSION_TRIPLE >= (3, 13)):
            raise TypeError(
                "Python Interpreter needs to be in 3.13 or greater; is %s"
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
