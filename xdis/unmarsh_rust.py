# Copyright (c) 2015-2021, 2024-2025 by Rocky Bernstein
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

"""RustPython version-independent Python object deserialization (unmarshal).

This is needed when the bytecode extracted is from
a different version than the currently-running Python.

When the running interpreter and the read-in bytecode are the same,
you can use Python's built-in ``marshal.loads()`` to produce a code
object.
"""

from struct import unpack
from typing import Any, Dict, List, Tuple, Union

from xdis.codetype.code313rust import Code313Rust, SourceLocation
from xdis.magics import magic_int2tuple
from xdis.unmarshal import (
    TYPE_ASCII,
    TYPE_ASCII_INTERNED,
    TYPE_BINARY_COMPLEX,
    TYPE_BINARY_FLOAT,
    TYPE_CODE,
    TYPE_DICT,
    TYPE_ELLIPSIS,
    TYPE_FALSE,
    TYPE_FROZENSET,
    TYPE_INT,
    TYPE_INT64,
    TYPE_INTERNED,
    TYPE_LIST,
    TYPE_LONG,
    TYPE_NONE,
    TYPE_NULL,
    TYPE_REF,
    TYPE_SET,
    TYPE_SHORT_ASCII,
    TYPE_SHORT_ASCII_INTERNED,
    TYPE_SLICE,
    TYPE_SMALL_TUPLE,
    TYPE_STOPITER,
    TYPE_STRING,
    TYPE_STRINGREF,
    TYPE_TRUE,
    TYPE_TUPLE,
    TYPE_UNICODE,
    TYPE_UNKNOWN,
    VersionIndependentUnmarshaller,
    compat_str,
)
from xdis.version_info import version_tuple_to_str

# Bit set on marshalType if we should
# add obj to intern_objects.
# FLAG_REF is the marshal.c name
FLAG_REF = 0x80

TYPE_COMPLEX_RUSTPYTHON = "y"
TYPE_FLOAT_RUSTPYTHON = "g"

# The keys in the following dictionary are unmarshal codes, like "s",
# "c", "<", etc. The values of the dictionary are names of routines
# to call that do the data unmarshaling.
#
# Note: we could eliminate the parameters if this were all inside a
# class.  This might be good from an efficiency standpoint, and bad
# from a functional-programming standpoint. Pick your poison.
# EDIT: I'm choosing efficiency over functional programming.
UNMARSHAL_DISPATCH_TABLE = {
    TYPE_ASCII: "ASCII",
    TYPE_ASCII_INTERNED: "ASCII_interned",
    TYPE_BINARY_COMPLEX: "binary_complex",
    TYPE_BINARY_FLOAT: "binary_float",
    TYPE_COMPLEX_RUSTPYTHON: "complex",
    TYPE_CODE: "code_rust",
    TYPE_DICT: "dict",
    TYPE_ELLIPSIS: "Ellipsis",
    TYPE_FALSE: "False",
    TYPE_FLOAT_RUSTPYTHON: "float",
    TYPE_FROZENSET: "frozenset",
    TYPE_INT64: "int64",
    TYPE_INT: "int32",
    TYPE_INTERNED: "interned",
    TYPE_LIST: "list",
    TYPE_LONG: "long",
    TYPE_NONE: "None",
    TYPE_NULL: "C_NULL",
    TYPE_REF: "object_reference",
    TYPE_SET: "set",
    TYPE_SHORT_ASCII: "short_ASCII",
    TYPE_SHORT_ASCII_INTERNED: "short_ASCII_interned",
    TYPE_SLICE: "slice",
    TYPE_SMALL_TUPLE: "small_tuple",
    TYPE_STOPITER: "stopIteration",
    TYPE_STRING: "string",
    TYPE_STRINGREF: "python2_string_reference",
    TYPE_TRUE: "True",
    TYPE_TUPLE: "tuple",
    TYPE_UNICODE: "unicode",
    TYPE_UNKNOWN: "unknown",
}

class MarshalError(Exception):
    pass

class VersionIndependentUnmarshallerRust(VersionIndependentUnmarshaller):
    def __init__(self, fp, magic_int, bytes_for_s, code_objects={}) -> None:
        """
        Marshal versions:
            4: [3.4a3, 3.13) (self.magic_int: 3280 onwards)
            5: [3.14, current) (self.magic_int: circa 3608)

        In Python 3, a ``bytes`` type is used for strings.
        """
        self.fp = fp
        self.magic_int = magic_int
        self.code_objects = code_objects

        # Save a list of offsets in the bytecode file where code
        # objects starts.
        self.code_to_file_offsets = {}

        # It is helpful to save the order in sets, frozensets and dictionary keys,
        # so that on writing a bytecode file we can duplicate this order.
        self.collection_order: Dict[Union[set, frozenset, dict], Tuple[Any]] = {}

        self.bytes_for_s = bytes_for_s
        self.version_triple = magic_int2tuple(self.magic_int)
        if self.version_triple >= (3, 14):
            self.marshal_version = 5
        elif (3, 14) > self.version_triple >= (3, 4):
            if self.magic_int in (12897,):
                self.marshal_version = 3
            else:
                self.marshal_version = 4
        else:
            assert False, f"version {version_tuple_to_str(self.version.triple)} is not a graal version"

        self.intern_strings = []
        self.intern_objects = []
        self.is_graal = False
        self.is_pypy = False
        self.is_rust = True

        self.UNMARSHAL_DISPATCH_TABLE = UNMARSHAL_DISPATCH_TABLE

    def t_code_rust(self, save_ref, bytes_for_s: bool = False) -> Code313Rust:
        # read instructions
        instr_count = self.read_int32()
        co_code = self.read_slice(instr_count * 2)

        instructions = [
            int.from_bytes(co_code[i:i+2], "little") for i in range(0, len(co_code), 2)
        ]

        # read locations
        loc_count = self.read_int32()
        locations: List[SourceLocation] = []
        for _ in range(loc_count):
            line = self.read_int32()
            if line == 0:
                raise MarshalError("invalid source location")
            # OneIndexed::new used in Rust requires line != 0
            char_off_zero_indexed = self.read_int32()
            locations.append(
                SourceLocation(
                    line=line,
                    character_offset=char_off_zero_indexed + 1  # convert from zero-indexed
                )
            )

        flags = self.read_int16()

        posonlyarg_count = self.read_int32()
        arg_count = self.read_int32()
        kwonlyarg_count = self.read_int32()

        # source_path
        src_len = self.t_int32(save_ref, bytes_for_s)
        source_path = self.read_string(src_len, False)

        first_line_raw = self.read_int32()
        first_line_number = None if first_line_raw == 0 else first_line_raw

        max_stackdepth = self.read_int32()

        obj_name_len = self.read_int32()
        obj_name = self.read_string(obj_name_len, False)

        qualname_len = self.read_int32()
        co_qualname = self.read_string(qualname_len, False)

        cell2arg = None
        if self.magic_int not in (12897,):
            cell2arg_len = self.read_int32()
            if cell2arg_len != 0:
                cell2arg = []
                for _ in range(cell2arg_len):
                    raw = self.read_int32()
                    # convert raw (u32) to signed i32
                    signed = raw if raw < (1 << 31) else raw - (1 << 32)
                    cell2arg.append(signed)

        # constants
        const_count = self.read_int32()
        constants = []
        for _ in range(const_count):
            # deserialize_value must exist in your runtime; it is the
            # counterpart of the Rust deserialize_value()
            constants.append(self.r_object(bytes_for_s=bytes_for_s))

        def read_names():
            n = self.read_int32()
            out = []
            for _ in range(n):
                length = self.read_int32()
                out.append(self.read_string(length, False))
            return out

        co_names = read_names()
        co_varnames = read_names()
        co_cellvars = read_names()
        co_freevars = read_names()
        co_nlocals = 0

        if self.magic_int not in (12897,):
            linetable_len = self.read_int32()
            co_linetable = self.read_slice(linetable_len)

            exceptiontable_len = self.read_int32()
            co_exceptiontable = self.read_slice(exceptiontable_len)
        else:
            co_linetable = b''
            co_exceptiontable = b''

        return Code313Rust(
            co_argcount=arg_count,
            co_posonlyargcount=posonlyarg_count,
            co_kwonlyargcount=kwonlyarg_count,
            co_nlocals=co_nlocals,
            co_stacksize=max_stackdepth,
            co_flags=flags,
            co_code=co_code,
            co_consts=constants,
            co_names=co_names,
            co_varnames=co_varnames,
            co_filename=source_path,
            co_name=obj_name,
            co_qualname=co_qualname,
            co_firstlineno=first_line_number,
            co_linetable=locations,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_exceptiontable=co_exceptiontable,
        )


    def read_int16(self):
        return int(unpack("<h", self.fp.read(2))[0])

    def read_int32(self):
        return int(unpack("<i", self.fp.read(4))[0])

    def read_slice(self, n: int) -> bytes:
        return self.fp.read(n)

    def read_string(self, n: int, bytes_for_s: bool=False) -> Union[bytes, str]:
        s = self.read_slice(n)
        if not bytes_for_s:
            s = compat_str(s)
        return s
