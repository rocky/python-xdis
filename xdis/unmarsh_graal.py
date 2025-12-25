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

"""Graal version-independent Python object deserialization (unmarshal).

This is needed when the bytecode extracted is from
a different version than the currently-running Python.

When the running interpreter and the read-in bytecode are the same,
you can use Python's built-in ``marshal.loads()`` to produce a code
object.
"""

import marshal
from struct import unpack, unpack_from

from xdis.codetype import to_portable
from xdis.magics import GRAAL3_MAGICS, magic_int2tuple
from xdis.unmarshal import (
    TYPE_ARRAY,
    TYPE_ASCII,
    TYPE_ASCII_INTERNED,
    TYPE_BINARY_COMPLEX,
    TYPE_BINARY_FLOAT,
    TYPE_COMPLEX,
    TYPE_DICT,
    TYPE_ELLIPSIS,
    TYPE_FALSE,
    TYPE_FLOAT,
    TYPE_FROZENSET,
    TYPE_GRAALPYTHON_CODE_UNIT,
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
)
from xdis.version_info import IS_GRAAL, PYTHON_VERSION_TRIPLE, version_tuple_to_str

# Graal Array types
TYPE_CODE_GRAAL = "C"
ARRAY_TYPE_BOOLEAN = "B"
ARRAY_TYPE_BYTE = "b"
ARRAY_TYPE_DOUBLE = "d"
ARRAY_TYPE_INT = "i"
ARRAY_TYPE_LONG = "l"
ARRAY_TYPE_OBJECT = "o"
ARRAY_TYPE_SHORT = "s"
ARRAY_TYPE_SLICE = ":"
ARRAY_TYPE_STRING = "S"


# The keys in the following dictionary are unmarshal codes, like "s",
# "c", "<", etc. The values of the dictionary are names of routines
# to call that do the data unmarshaling.
#
# Note: we could eliminate the parameters if this were all inside a
# class.  This might be good from an efficiency standpoint, and bad
# from a functional-programming standpoint. Pick your poison.
# EDIT: I'm choosing efficiency over functional programming.
UNMARSHAL_DISPATCH_TABLE = {
    TYPE_ARRAY: "graal_readArray",
    TYPE_ASCII: "ASCII",
    TYPE_ASCII_INTERNED: "ASCII_interned",
    TYPE_BINARY_COMPLEX: "binary_complex",
    TYPE_BINARY_FLOAT: "binary_float",
    TYPE_CODE_GRAAL: "code_graal",
    TYPE_COMPLEX: "complex",
    TYPE_DICT: "dict",
    TYPE_ELLIPSIS: "Ellipsis",
    TYPE_FALSE: "False",
    TYPE_FLOAT: "float",
    TYPE_FROZENSET: "frozenset",
    TYPE_GRAALPYTHON_CODE_UNIT: "graal_CodeUnit",
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

# Used by graal
JAVA_MARSHAL_SHIFT = 15
JAVA_MARSHAL_BASE = 1 << JAVA_MARSHAL_SHIFT

class VersionIndependentUnmarshallerGraal(VersionIndependentUnmarshaller):
    def __init__(self, fp, magic_int, bytes_for_s, code_objects={}) -> None:
        """
        Marshal versions:
            2: [2.5, 3.4a0) (self.magic_int: 62071 until 3250)
            3: [3.4a0, 3.4a3) (self.magic_int: 3250 until 3280)
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
        self.collection_order = {}

        self.bytes_for_s = bytes_for_s
        self.version_triple = magic_int2tuple(self.magic_int)
        if self.version_triple >= (3, 14):
            self.marshal_version = 5
        elif (3, 14) > self.version_triple >= (3, 4):
            if self.magic_int in (3250, 3260, 3270):
                self.marshal_version = 3
            else:
                self.marshal_version = 4
        elif (3, 4) > self.version_triple >= (2, 5):
            self.marshal_version = 2
        else:
            assert False, (
                "version %s is not a graal version" %
                version_tuple_to_str(self.version.triple)
                )

        self.intern_strings = []
        self.intern_objects = []
        self.is_graal = True
        self.is_pypy = False
        self.is_rust = False

        # Graal code data seems to be split in two places.
        # The outer part is a TYPE_GRAALPYTHON_CODE,
        # while the inner part is in TYPE_GRAALPYTHON_CODE_UNIT
        # Save the out information so that the inner information
        # can use this when building a code type.

        # in a TYPE_GRAAL
        self.graal_code_info = {}

        self.UNMARSHAL_DISPATCH_TABLE = UNMARSHAL_DISPATCH_TABLE

    # Python equivalents for graal unmarshal routines.
    def t_graal_readArray(self, save_ref: bool, bytes_for_s: bool) -> tuple:
        """
        Python equivalent of Python Graal's readArray() from
        MarshalModuleBuiltins.java

        Array object unmarshalling read routine.  Reads from self.fp
        the next byte which is a key in ARRAY_TYPE defined above.

        Parameter save_ref indicates whether to save the resulting object in
        our internal object cache.
        """
        byte1 = ord(self.fp.read(1))

        marshal_type = chr(byte1)

        # print(marshal_type)  # debug

        if marshal_type == ARRAY_TYPE_BOOLEAN:
                ret = self.graal_readBooleanArray()
        elif marshal_type == ARRAY_TYPE_DOUBLE:
            ret = self.graal_readDoubleArray()
        elif marshal_type == ARRAY_TYPE_INT:
            ret = self.graal_readIntArray()
        elif marshal_type == ARRAY_TYPE_OBJECT:
            ret = self.graal_readObjectArray()
        elif marshal_type == ARRAY_TYPE_LONG:
            ret = self.graal_readLongArray()
        elif marshal_type == ARRAY_TYPE_STRING:
            ret = self.graal_readStringArray()
        else:
            # The underscore '_' acts as a wildcard
            # It matches anything if no previous case did (the 'default' case)
            print("XXX Whoah %s" % marshal_type)
            ret = tuple()
        if save_ref:
            if isinstance(ret, tuple):
                self.intern_objects += list(ret)
            else:
                self.intern_objects.append(ret)
        return ret

    def graal_readBigInteger(self):
        """
        Reads a marshaled big integer from the input stream.
        """
        negative = False
        sz = self.read_uint32() # Get the size in shorts
        if sz < 0:
            negative = True
            sz = -sz

        # size is in shorts, convert to size in bytes
        sz *= 2

        data = bytes([self.graal_readByte() for _ in range(sz)])

        i = 0

        # Read the first 2 bytes as a 16-bit signed integer (short)
        # '>h' specifies big-endian signed short
        digit = unpack_from('>h', data, i)[0]
        i += 2

        # Python int handles arbitrarily large numbers
        result = digit

        while i < sz:
            # Calculate the power based on the number of shorts processed so far
            power = i // 2
            # Read the next 2 bytes as a 16-bit signed integer
            digit = unpack_from('>h', data, i)[0]
            i += 2

            # In Python, int supports all these operations directly
            # The Java code effectively reconstructs the number using base 2^16 (MARSHAL_BASE)
            term = digit * (JAVA_MARSHAL_BASE ** power)
            result += term

        if negative:
            return -result
        else:
            return result

    def graal_readBooleanArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readBooleanArray() from
        MarshalModuleBuiltins.java
        """
        length: int = self.read_uint32()
        return tuple([bool(self.graal_readByte()) for _ in range(length)])

    def graal_readByte(self) -> int:
        """
        Python equivalent of Python Graal's readBytes() from
        MarshalModuleBuiltins.java
        """
        return ord(unpack("c", self.fp.read(1))[0])

    def graal_readBytes(self) -> bytes:
        """
        Python equivalent of Python Graal's readBytes() from
        MarshalModuleBuiltins.java
        """
        length: int = self.read_uint32()
        return bytes([self.graal_readByte() for _ in range(length)])

    def graal_readDoubleArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readDoubleArray() from
        MarshalModuleBuiltins.java
        """
        length: int = self.read_uint32()
        return tuple([self.read_float() for _ in range(length)])

    def graal_readIntArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readIntArray() from
        MarshalModuleBuiltins.java
        """
        length: int = self.read_uint32()
        return tuple([self.read_int32() for _ in range(length)])

    def graal_readLong(self) -> int:
        """
        Python equivalent of Python Graal's readLongt() from
        MarshalModuleBuiltins.java
        """
        return int(unpack("<q", self.fp.read(8))[0])

    def graal_readLongArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readLongt() from
        MarshalModuleBuiltins.java
        """
        length = int(unpack("<i", self.fp.read(4))[0])
        return tuple([self.graal_readLong() for _ in range(length)])

    def graal_readObjectArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """

        length = int(unpack("<i", self.fp.read(4))[0])
        # # Debug code
        # result = []
        # for i in range(length):
        #     try:
        #         result.append(self.r_object(bytes_for_s=False))
        #     except:
        #         breakpoint()
        # return tuple(result)
        return tuple([self.r_object(bytes_for_s=False) for _ in range(length)])

    def graal_readString(self) -> str:
        """
        Python equvalent of Python Graal's readString() from
        MarshalModuleBuiltins.java
        """
        strsize = unpack("<i", self.fp.read(4))[0]
        return self.fp.read(strsize).decode("utf-8", errors="ignore")

    def graal_readStringArray(self) -> tuple:
        """
        Python equvalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """
        length: int = self.read_uint32()
        return tuple([self.graal_readString() for _ in range(length)])

    def graal_readSparseTable(self) -> dict:
        """
        Python equvalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """
        self.read_uint32()  # the length return value isn't used.
        table = {}  # new int[length][];
        while True:
            i = self.read_int32()
            if i == -1:
                return table
            table[i] = self.graal_readIntArray()

    def t_code_graal(self, save_ref, bytes_for_s: bool = False):
        """
        Graal Python code. This has fewer fields than Python
        code. In particular, instructions are JVM bytecode.
        """

        # Go back one byte to TYPE_CODE "C" or "C" with the FLAG_REF
        # set.
        code_offset_in_file = self.fp.tell() - 1

        # Below, the value None (slot for a code object value), will
        # be replaced by the actual code in variable `ret` after it
        # has been built.
        ret, i = self.r_ref_reserve(None, save_ref)

        self.version_triple = magic_int2tuple(self.magic_int)

        # This is graal 312 Java code for writing a bytecode file
        # after the file header info had been read:
        #   writeByte(TYPE_GRAALPYTHON_CODE | flag);
        #   writeString(c.getFilename());
        #   writeInt(c.getFlags());
        #   writeBytes(c.getCodestring());
        #   writeInt(c.getFirstLineNo());
        #   byte[] lnotab = c.getLinetable();
        #   if (lnotab == null) {
        #         lnotab = PythonUtils.EMPTY_BYTE_ARRAY;
        #   }
        #   writeBytes(lnotab);

        self.graal_code_info["co_filename"] = self.graal_readString()
        self.graal_code_info["co_flags"] = self.t_int32(False, bytes_for_s=False)
        co_codeunit_position = self.graal_code_info["co_codeunit_position"] = (
            self.fp.tell() + 4
        )
        co_codeunit_string = self.graal_readBytes()
        # Determine if we are Graal 3.10, 3.11, or 3.12 ...
        if chr(co_codeunit_string[0]) != TYPE_GRAALPYTHON_CODE_UNIT:
            # Determine if we are Graal 3.10, 3.11
            co_codeunit_string = b"U" + co_codeunit_string
            if self.version_triple != (3, 10, 8):
                self.version_triple = (3, 11, 7)
        else:
            self.version_triple = (3, 12, 8)

        self.graal_code_info["co_firstlineno"] = self.t_int32(False, bytes_for_s=False)
        self.graal_code_info["co_lnotab"] = self.t_string(False, bytes_for_s=True)

        # Go back to code position and parse CodeUnit
        saved_position = self.fp.tell()
        self.fp.seek(co_codeunit_position)
        if self.version_triple == (3, 12, 8):
            code = self.r_object(bytes_for_s=False)
        else:
            code = self.t_graal_CodeUnit(save_ref=False, bytes_for_s=False)
        assert self.graal_code_info["co_flags"] == code.co_flags

        # FIXME: add an assert self.fp.tell() has advanced to save_position?
        self.fp.seek(saved_position)

        code.graal_instr_str = ""
        if IS_GRAAL and PYTHON_VERSION_TRIPLE == self.version_triple:
            try:
                graal_instr_str = str(marshal.loads(co_codeunit_string))
            except Exception:
                pass
            else:
                code.graal_instr_str = graal_instr_str

        self.code_to_file_offsets[code] = (
            code_offset_in_file,
            self.code_to_file_offsets[code][0],
        )
        self.code_objects[str(code)] = code

        return self.r_ref_insert(code, i)

    def t_graal_CodeUnit(self, save_ref, bytes_for_s: bool = False):
        """
        Graal Python code. This has fewer fields than Python
        code. Graal Python Bytecode is similar to Python Bytecode for
        a given version, things are a little different, especially when it comes
        to collections. Graal has intructions for homogeneous arrays.

        Note that Graal's BytecodeCodeUnit has a dumpBytecode() method
        to show assembly instructions.
        """

        graal_bytecode_version = self.graal_readByte()
        assert (21000 + graal_bytecode_version * 10) in GRAAL3_MAGICS
        if graal_bytecode_version in (26,):
            self.version_triple = (3, 8, 5)

        other_fields = {}

        # This is Java code for how a CodeUnit (type "U") is read
        # TruffleString name = readString();
        # TruffleString qualname = readString();
        # int argCount = readInt();
        # int kwOnlyArgCount = readInt();
        # int positionalOnlyArgCount = readInt();
        # int stacksize = readInt();
        # byte[] code = readBytes();
        # byte[] srcOffsetTable = readBytes();
        # int flags = readInt();

        co_name = self.graal_readString()
        co_qualname = self.graal_readString()
        co_argcount = self.read_uint32()
        co_kwonlyargcount = self.read_uint32()
        co_posonlyargcount = self.read_uint32()

        co_stacksize = self.read_uint32()
        co_code_offset_in_file = self.fp.tell()
        co_code = self.graal_readBytes()
        other_fields["srcOffsetTable"] = self.graal_readBytes()
        co_flags = self.read_uint32()

        # writeStringArray(code.names);
        # writeStringArray(code.varnames);
        # writeStringArray(code.cellvars);
        # writeStringArray(code.freevars);

        co_names = self.graal_readStringArray()
        co_varnames = self.graal_readStringArray()
        co_cellvars = self.graal_readStringArray()
        co_freevars = self.graal_readStringArray()

        # int[] cell2arg = readIntArray();
        # if (cell2arg.length == 0) {
        #     cell2arg = null;
        #     }
        # Object[] constants = readObjectArray();

        other_fields["cell2arg"] = self.graal_readIntArray()
        co_consts = self.graal_readObjectArray()

        # The data from the below is not used, but we run the
        # the extraction to keep the self.fp location where it should for
        # the situation that we have code objects inside the codes' co_consts
        # table marshaled as an ObjectArray.

        # long[] primitiveConstants = readLongArray();
        # int[] exceptionHandlerRanges = readIntArray();
        # int conditionProfileCount = readInt();
        # int startLine = readInt();
        # int startColumn = readInt();
        # int endLine = readInt();
        # int endColumn = readInt();
        # byte[] outputCanQuicken = readBytes();
        # byte[] variableShouldUnbox = readBytes();
        # int[][] generalizeInputsMap = readSparseTable();
        # int[][] generalizeVarsMap = readSparseTable();

        other_fields["primitiveConstants"] = self.graal_readLongArray()
        other_fields["exception_handler_ranges"] = self.graal_readIntArray()
        other_fields["condition_profileCount"] = self.read_uint32()
        other_fields["startLine"] = self.read_uint32()
        other_fields["startColumn"] = self.read_uint32()
        other_fields["endLine"] = self.read_uint32()
        other_fields["endColumn"] = self.read_uint32()
        other_fields["outputCanQuicken"] = self.graal_readBytes()
        other_fields["variableShouldUnbox"] = self.graal_readBytes()
        other_fields["generalizeInputsMap"] = self.graal_readSparseTable()
        other_fields["generalizeVarsMap"] = self.graal_readSparseTable()

        code = to_portable(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=co_kwonlyargcount,
            co_nlocals=0,
            co_stacksize=co_stacksize,
            co_flags=co_flags,
            co_code=co_code,
            co_consts=co_consts,
            co_names=co_names,
            co_varnames=co_varnames,
            co_filename=self.graal_code_info["co_filename"],
            co_name=co_name,
            co_qualname=co_qualname,
            co_firstlineno=self.graal_code_info["co_firstlineno"],
            co_lnotab=self.graal_code_info["co_lnotab"],
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_exceptiontable="",
            version_triple=self.version_triple,
            collection_order=self.collection_order,
            reference_objects=set(),
            other_fields=other_fields,
        )

        self.code_to_file_offsets[code] = tuple(
            [self.graal_code_info["co_codeunit_position"], co_code_offset_in_file]
        )

        # if graal_bytecode_version == 26:
        #     from xdis.bytecode_graal import get_instructions_bytes_graal
        #     from xdis.opcodes import opcode_38graal
        #     get_instructions_bytes_graal(code, opcode_38graal)
        return code
