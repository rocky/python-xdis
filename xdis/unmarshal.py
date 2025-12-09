# Copyright (c) 2015-2021, 2024-2025 by Rocky Bernstein
# Copyright (c) 2000-2002 by hartmut Goebel <h.goebel@crazy-compilers.com>
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

"""CPython magic- and version-independent Python object
deserialization (unmarshal).

This is needed when the bytecode extracted is from
a different version than the currently-running Python.

When the running interpreter and the read-in bytecode are the same,
you can use Python's built-in ``marshal.loads()`` to produce a code
object.
"""

import io
import marshal
import sys
from struct import unpack
from types import EllipsisType
from typing import Any, Dict, Tuple, Union

from xdis.codetype import to_portable
from xdis.cross_types import LongTypeForPython3, UnicodeForPython3
from xdis.magics import GRAAL3_MAGICS, PYPY3_MAGICS, RUSTPYTHON_MAGICS, magic_int2tuple
from xdis.version_info import IS_GRAAL, PYTHON_VERSION_TRIPLE, version_tuple_to_str


def long(n: int) -> LongTypeForPython3:
    return LongTypeForPython3(n)

    # FIXME: we should write a bytes() class with a repr
    # that prints the b'' prefix so that Python2 can
    # print out Python3 code correctly


# Bit set on marshalType if we should
# add obj to intern_objects.
# FLAG_REF is the marshal.c name
FLAG_REF = 0x80

TYPE_ASCII = "a"  # since 3.4
TYPE_ASCII_INTERNED = "A"  # Version 4. since 3.4
TYPE_ARRAY = "]"  # Graal Python uses this
TYPE_BIG_INTEGER = "B"  # Graal Python uses this.
TYPE_BINARY_COMPLEX = "y"  # 3.x; Version 0 uses TYPE_COMPLEX instead
TYPE_BINARY_FLOAT = "g"  # Version 0 uses TYPE_FLOAT instead
TYPE_CODE = "c"
TYPE_CODE_OLD = "C"  # used in Python 1.0 - 1.2. Graal Python uses this too.
TYPE_COMPLEX = "x"  # Version 0 only. Not in use after Python 2.4
TYPE_DICT = "{"
TYPE_ELLIPSIS = "."
TYPE_FALSE = "F"
TYPE_FLOAT = "f"  # Version 0 only. Not in use after Python 2.4
TYPE_FROZENSET = ">"  # Since version 2.
TYPE_GRAAL_ARRAY = "]"  # since 3.4
TYPE_GRAALPYTHON_CODE = "C"  # Duplicate. Graal Python uses this for its code.
TYPE_GRAALPYTHON_CODE_UNIT = "U"  # Graal Python uses this.
TYPE_INT = "i"  # All versions. 32-bit encoding.
TYPE_INT64 = "I"  # Python 3.4 removed this
TYPE_INTERNED = "t"  # 1+
TYPE_LIST = "["
TYPE_LONG = "l"
TYPE_NONE = "N"
TYPE_NULL = "0"
TYPE_REF = "r"  # Version 3. Since 3.4 (and a little before?)
TYPE_SET = "<"  # Since Version 2.
TYPE_SHORT_ASCII = "z"  # Version 4. since 3.4
TYPE_SHORT_ASCII_INTERNED = "Z"  # Version 3. since 3.4
TYPE_SLICE = ":"  # Version 5. Since 3.14
TYPE_SMALL_TUPLE = ")"  # Version 3. since 3.4
TYPE_STOPITER = "S"
TYPE_STRING = "s"  # String in Python 2. In Python 3 this is Bytes.
TYPE_STRINGREF = "R"  # Python 2
TYPE_TRUE = "T"
TYPE_TUPLE = "("  # See also TYPE_SMALL_TUPLE
TYPE_UNICODE = "u"
TYPE_UNKNOWN = "?"

# Graal Array types
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
    TYPE_CODE: "code",
    TYPE_CODE_OLD: "code_old_or_graal",  # Older Python code and Graal
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
    TYPE_SMALL_TUPLE: "small_tuple",
    TYPE_STOPITER: "stopIteration",
    TYPE_STRING: "string",
    TYPE_STRINGREF: "python2_string_reference",
    TYPE_TRUE: "True",
    TYPE_TUPLE: "tuple",
    TYPE_UNICODE: "unicode",
    TYPE_UNKNOWN: "unknown",
}


def compat_str(s: Union[str, bytes]) -> Union[str, bytes]:
    """
    This handles working with strings between Python2 and Python3.
    """
    if isinstance(s, bytes):
        return s.decode("utf-8", errors="ignore")
    elif not isinstance(s, str):
        return str(s)
    else:
        return s


def compat_u2s(u) -> str:
    return str(u)


class _VersionIndependentUnmarshaller:
    def __init__(self, fp, magic_int, bytes_for_s, code_objects={}) -> None:
        """
        Marshal versions:
            0/Historical: Until 2.4/magic int 62041
            1: [2.4, 2.5) (self.magic_int: 62041 until 62071)
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
        self.collection_order: Dict[Union[set, frozenset, dict], Tuple[Any]] = {}

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
        elif (2, 5) > self.version_triple >= (2, 4):
            self.marshal_version = 1
        else:
            self.marshal_version = 0

        self.intern_strings = []
        self.intern_objects = []
        self.is_graal = magic_int in GRAAL3_MAGICS
        self.is_pypy = magic_int in PYPY3_MAGICS
        self.is_rust = magic_int in RUSTPYTHON_MAGICS

        # Graal code data seems to be split in two places.
        # The outer part is a TYPE_GRAALPYTHON_CODE,
        # while the inner part is in TYPE_GRAALPYTHON_CODE_UNIT
        # Save the out information so that the inner information
        # can use this when building a code type.

        # in a TYPE_GRAAL
        self.graal_code_info = {}

        if magic_int in RUSTPYTHON_MAGICS:
            raise NotImplementedError(
                f"RustPython {version_tuple_to_str(self.version_triple)} is not supported yet."
            )

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

        match marshal_type:
            # case "B":
            #     ret = tuple()
            # case "b":
            #     return "OK"
            case "d":
                ret = self.graal_readDoubleArray()
            case "i":
                ret = self.graal_readIntArray()
            case "o":
                ret = self.graal_readObjectArray()
            case "l":
                ret = self.graal_readLongArray()
            # case "s":
            #     return "Internal server error"
            case "S":
                ret = self.graal_readStringArray()
            case _:
                # The underscore '_' acts as a wildcard
                # It matches anything if no previous case did (the 'default' case)
                print(f"XXX Whoah {marshal_type}")
                ret = tuple()
        if save_ref:
            self.intern_objects.append(ret)
        return ret

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
        length: int = unpack("<i", self.fp.read(4))[0]
        return bytes([self.graal_readByte() for _ in range(length)])

    def graal_readDouble(self) -> float:
        """
        Python equivalent of Python Graal's readDouble() from
        MarshalModuleBuiltins.java
        """
        return unpack("<d", self.fp.read(8))[0]

    def graal_readDoubleArray(self) -> tuple[float, ...]:
        """
        Python equivalent of Python Graal's readDoubleArray() from
        MarshalModuleBuiltins.java
        """
        length: int = int(unpack("<i", self.fp.read(4))[0])
        return tuple([self.graal_readDouble() for _ in range(length)])

    def graal_readInt(self) -> int:
        """
        Python equivalent of Python Graal's readInt() from
        MarshalModuleBuiltins.java
        """
        return int(unpack("<i", self.fp.read(4))[0])

    def graal_readIntArray(self) -> tuple[int, ...]:
        """
        Python equivalent of Python Graal's readIntArray() from
        MarshalModuleBuiltins.java
        """
        length: int = int(unpack("<i", self.fp.read(4))[0])
        return tuple([self.graal_readInt() for _ in range(length)])

    def graal_readLong(self) -> int:
        """
        Python equivalent of Python Graal's readLongt() from
        MarshalModuleBuiltins.java
        """
        return int(unpack("<q", self.fp.read(8))[0])

    def graal_readLongArray(self) -> tuple[int, ...]:
        """
        Python equivalent of Python Graal's readLongt() from
        MarshalModuleBuiltins.java
        """
        length: int = int(unpack("<i", self.fp.read(4))[0])
        return tuple([self.graal_readLong() for _ in range(length)])

    def graal_readObjectArray(self) -> tuple:
        """
        Python equivalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """

        length: int = int(unpack("<i", self.fp.read(4))[0])
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
        strsize: int = unpack("<i", self.fp.read(4))[0]
        return self.fp.read(strsize).decode("utf-8", errors="ignore")

    def graal_readStringArray(self) -> tuple[str, ...]:
        """
        Python equvalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """
        length: int = self.graal_readInt()
        return tuple([self.graal_readString() for _ in range(length)])

    def graal_readSparseTable(self) -> Dict[int, tuple]:
        """
        Python equvalent of Python Graal's readObjectArray() from
        MarshalModuleBuiltins.java
        """
        self.graal_readInt()  # the length return value isn't used.
        table = {}  # new int[length][];
        while True:
            i = self.graal_readInt()
            if i == -1:
                return table
            table[i] = self.graal_readIntArray()

    def load(self):
        """
        ``marshal.load()`` written in Python. When the Python bytecode magic loaded is the
        same magic for the running Python interpreter, we can simply use the
        Python-supplied marshal.load().

        However, we need to use this when versions are different since the internal
        code structures are different. Sigh.
        """

        if self.marshal_version == 0:
            self.intern_strings = []
        if self.marshal_version < 3:
            assert self.intern_objects == []

        return self.r_object()

    # Python 3.4+ support for reference objects.
    # The names follow marshal.c
    def r_ref_reserve(self, obj, save_ref):
        i = None
        if save_ref:
            i = len(self.intern_objects)
            self.intern_objects.append(obj)
        return obj, i

    def r_ref_insert(self, obj, i: int | None):
        if i is not None:
            if not isinstance(obj, (set, list)):
                # I am not sure if this is right...
                # We can't turn into a set a list that contains a
                # list or a set. So skip these, for now
                self.intern_objects[i] = obj
        return obj

    def r_ref(self, obj, save_ref):
        if save_ref:
            self.intern_objects.append(obj)
        return obj

    # In marshal.c this is one big case statement
    # FIXME: remove bytes_fo_s parameter.
    # Now that we have git branches, isolated by Python version.
    # This is only needed in the Python 2.4 - 2.7 code branch.
    def r_object(self, bytes_for_s: bool = False):
        """
        Main object unmarshaling read routine.  Reads from self.fp
        the next byte which is a key in UNMARSHAL_DISPATCH_TABLE
        defined above clearing the high-order bit, FLAG_REF.
        FLAG_REF indicates whether to save the resulting object in
        our internal object cache.
        """
        byte1 = ord(self.fp.read(1))

        # FLAG_REF indicates whether we "intern" or
        # save a reference to the object.
        # byte1 without that reference is the
        # marshal type code, an ASCII character.
        save_ref = False
        if byte1 & FLAG_REF:
            # Since 3.4, "flag" is the marshal.c name
            save_ref = True
            byte1 = byte1 & (FLAG_REF - 1)
        marshal_type = chr(byte1)

        # print(marshal_type)  # debug

        if marshal_type in UNMARSHAL_DISPATCH_TABLE:
            func_suffix = UNMARSHAL_DISPATCH_TABLE[marshal_type]
            unmarshal_func = getattr(self, "t_" + func_suffix)
            return unmarshal_func(save_ref, bytes_for_s)
        else:
            try:
                sys.stderr.write(
                    "Unknown type %i (hex %x) %c\n"
                    % (ord(marshal_type), ord(marshal_type), marshal_type)
                )
            except TypeError:
                sys.stderr.write(
                    "Unknown type %i %c\n" % (ord(marshal_type), marshal_type)
                )

        return

    # In C this NULL. Not sure what it should
    # translate here. Note NULL != None which is below
    def t_C_NULL(self, save_ref, bytes_for_s: bool = False) -> None:
        return None

    def t_None(self, save_ref, bytes_for_s: bool = False) -> None:
        return None

    def t_stopIteration(
        self, save_ref, bytes_for_s: bool = False
    ) -> type[StopIteration]:
        return StopIteration

    def t_Ellipsis(self, save_ref, bytes_for_s: bool = False) -> EllipsisType:
        return Ellipsis

    def t_False(self, save_ref, bytes_for_s: bool = False) -> bool:
        return False

    def t_True(self, save_ref, bytes_for_s: bool = False) -> bool:
        return True

    def t_int32(self, save_ref, bytes_for_s: bool = False):
        return self.r_ref(int(unpack("<i", self.fp.read(4))[0]), save_ref)

    def t_long(self, save_ref, bytes_for_s: bool = False):
        n = unpack("<i", self.fp.read(4))[0]
        if n == 0:
            return long(0)
        size = abs(n)
        d = long(0)
        for j in range(0, size):
            md = int(unpack("<h", self.fp.read(2))[0])
            # This operation and turn "d" from a long back
            # into an int.
            d += md << j * 15
            d = long(d)
        if n < 0:
            d = long(d * -1)

        return self.r_ref(d, save_ref)

    # Python 3.4 removed this.
    def t_int64(self, save_ref, bytes_for_s: bool = False):
        obj = unpack("<q", self.fp.read(8))[0]
        if save_ref:
            self.intern_objects.append(obj)
        return obj

    # float - Seems not in use after Python 2.4
    def t_float(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("B", self.fp.read(1))[0]
        s = self.fp.read(strsize)
        return self.r_ref(float(s), save_ref)

    def t_binary_float(self, save_ref, bytes_for_s: bool = False):
        return self.r_ref(float(unpack("<d", self.fp.read(8))[0]), save_ref)

    def t_complex(self, save_ref, bytes_for_s: bool = False):
        def unpack_pre_24() -> float:
            return float(self.fp.read(unpack("B", self.fp.read(1))[0]))

        def unpack_newer() -> float:
            return float(self.fp.read(unpack("<i", self.fp.read(4))[0]))

        get_float = unpack_pre_24 if self.magic_int <= 62061 else unpack_newer

        real = get_float()
        imag = get_float()
        return self.r_ref(complex(real, imag), save_ref)

    def t_binary_complex(self, save_ref, bytes_for_s: bool = False):
        # binary complex
        real = unpack("<d", self.fp.read(8))[0]
        imag = unpack("<d", self.fp.read(8))[0]
        return self.r_ref(complex(real, imag), save_ref)

    def t_string(self, save_ref, bytes_for_s: bool):
        """
        Get a string from the bytecode file and save the string in ``save_ref``.

        In Python3, this is a ``bytes`` type.  In Python2, it is a string type;
        ``bytes_for_s`` is True when a Python 3 interpreter is reading Python 2 bytecode.
        """
        strsize = unpack("<i", self.fp.read(4))[0]
        s = self.fp.read(strsize)
        if not bytes_for_s:
            s = compat_str(s)
        return self.r_ref(s, save_ref)

    # Python 3.4
    def t_ASCII_interned(self, save_ref, bytes_for_s: bool = False):
        """
        There are true strings in Python3 as opposed to
        bytes. "interned" just means we keep a reference to
        the string.
        """
        # FIXME: check
        strsize = unpack("<i", self.fp.read(4))[0]
        interned = compat_str(self.fp.read(strsize))
        self.intern_strings.append(interned)
        return self.r_ref(interned, save_ref)

    # Since Python 3.4
    def t_ASCII(self, save_ref, bytes_for_s: bool = False):
        """
        There are true strings in Python3 as opposed to
        bytes.
        """
        strsize = unpack("<i", self.fp.read(4))[0]
        s = self.fp.read(strsize)
        s = compat_str(s)
        return self.r_ref(s, save_ref)

    # Since Python 3.4
    def t_short_ASCII(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("B", self.fp.read(1))[0]
        return self.r_ref(compat_str(self.fp.read(strsize)), save_ref)

    # Since Python 3.4
    def t_short_ASCII_interned(self, save_ref, bytes_for_s: bool = False):
        # FIXME: check
        strsize = unpack("B", self.fp.read(1))[0]
        interned = compat_str(self.fp.read(strsize))
        self.intern_strings.append(interned)
        return self.r_ref(interned, save_ref)

    def t_interned(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("<i", self.fp.read(4))[0]
        interned = compat_str(self.fp.read(strsize))
        self.intern_strings.append(interned)
        return self.r_ref(interned, save_ref)

    def t_unicode(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("<i", self.fp.read(4))[0]
        unicodestring = self.fp.read(strsize)
        if self.version_triple < (3, 0):
            string = UnicodeForPython3(unicodestring)
        else:
            string = unicodestring.decode()

        return self.r_ref(string, save_ref)

    # Since Python 3.4
    def t_small_tuple(self, save_ref, bytes_for_s: bool = False):
        # small tuple - since Python 3.4
        tuplesize = unpack("B", self.fp.read(1))[0]
        ret, i = self.r_ref_reserve(tuple(), save_ref)
        while tuplesize > 0:
            ret += (self.r_object(bytes_for_s=bytes_for_s),)
            tuplesize -= 1
            pass
        return self.r_ref_insert(ret, i)

    def t_tuple(self, save_ref, bytes_for_s: bool = False):
        tuplesize = unpack("<i", self.fp.read(4))[0]
        ret = self.r_ref(tuple(), save_ref)
        while tuplesize > 0:
            ret += (self.r_object(bytes_for_s=bytes_for_s),)
            tuplesize -= 1
        return ret

    def t_list(self, save_ref, bytes_for_s: bool = False):
        # FIXME: check me
        n = unpack("<i", self.fp.read(4))[0]
        ret = self.r_ref(list(), save_ref)
        while n > 0:
            ret += (self.r_object(bytes_for_s=bytes_for_s),)
            n -= 1
        return ret

    def t_frozenset(self, save_ref, bytes_for_s: bool = False):
        setsize = unpack("<i", self.fp.read(4))[0]
        collection, i = self.r_ref_reserve([], save_ref)
        while setsize > 0:
            collection.append(self.r_object(bytes_for_s=bytes_for_s))
            setsize -= 1
        final_frozenset = frozenset(collection)
        # Note the order of the frozenset elements.
        self.collection_order[final_frozenset] = tuple(collection)
        return self.r_ref_insert(final_frozenset, i)

    def t_set(self, save_ref, bytes_for_s: bool = False):
        setsize = unpack("<i", self.fp.read(4))[0]
        ret, i = self.r_ref_reserve(tuple(), save_ref)
        while setsize > 0:
            ret += (self.r_object(bytes_for_s=bytes_for_s),)
            setsize -= 1
        return self.r_ref_insert(set(ret), i)

    def t_dict(self, save_ref, bytes_for_s: bool = False):
        ret = self.r_ref(dict(), save_ref)
        # dictionary
        while True:
            key = self.r_object(bytes_for_s=bytes_for_s)
            if key is None:
                break
            val = self.r_object(bytes_for_s=bytes_for_s)
            if val is None:
                break
            ret[key] = val
            pass
        return ret

    def t_python2_string_reference(self, save_ref, bytes_for_s: bool = False):
        refnum = unpack("<i", self.fp.read(4))[0]
        return self.intern_strings[refnum]

    def t_slice(self, save_ref, bytes_for_s: bool = False):
        """TYPE_SLICE introducted in Marshal version 5"""
        retval, idx = self.r_ref_reserve(slice(None, None, None), save_ref)

        if idx and idx < 0:
            return

        # FIXME: we currently can't disambiguate between NULL and None.
        #        marshal.c exits early if start, stop, or step are NULL.
        #        https://github.com/python/cpython/blob/2dac9e6016c81abbefa4256253ff5c59b29378a7/Python/marshal.c#L1657
        start = self.r_object(bytes_for_s=bytes_for_s)
        stop = self.r_object(bytes_for_s=bytes_for_s)
        step = self.r_object(bytes_for_s=bytes_for_s)

        retval = slice(start, stop, step)
        return self.r_ref_insert(retval, idx)

    def t_code(self, save_ref, bytes_for_s: bool = False):
        """
        CPython and PyPy code type in all of its horrific variations.
        """
        # FIXME: use tables to simplify this?

        # Go back one byte to TYPE_CODE "c" or "c" with the FLAG_REF
        # set.
        code_offset_in_file = self.fp.tell() - 1

        # Below, the value None (slot for a code object value), will
        # be replaced by the actual code in variable `ret` after it
        # has been built.
        ret, i = self.r_ref_reserve(None, save_ref)

        self.version_triple = magic_int2tuple(self.magic_int)

        if self.version_triple >= (2, 3):
            co_argcount = unpack("<i", self.fp.read(4))[0]
        elif self.version_triple >= (1, 3):
            co_argcount = unpack("<h", self.fp.read(2))[0]
        else:
            co_argcount = 0

        if self.version_triple >= (3, 8):
            co_posonlyargcount = (
                0
                if self.magic_int in (3400, 3401, 3410, 3411)
                else unpack("<i", self.fp.read(4))[0]
            )
        else:
            co_posonlyargcount = None

        if self.version_triple >= (3, 0):
            kwonlyargcount = unpack("<i", self.fp.read(4))[0]
        else:
            kwonlyargcount = 0

        co_nlocals = 0
        if self.version_triple < (3, 11) or (
            self.version_triple[:2] == (3, 11) and self.is_pypy
        ):
            if self.version_triple >= (2, 3):
                co_nlocals = unpack("<i", self.fp.read(4))[0]
            elif self.version_triple >= (1, 3):
                co_nlocals = unpack("<h", self.fp.read(2))[0]

        if self.version_triple >= (2, 3):
            co_stacksize = unpack("<i", self.fp.read(4))[0]
        elif self.version_triple >= (1, 5):
            co_stacksize = unpack("<h", self.fp.read(2))[0]
        else:
            co_stacksize = 0

        if self.version_triple >= (2, 3):
            co_flags = unpack("<i", self.fp.read(4))[0]
        elif self.version_triple >= (1, 3):
            co_flags = unpack("<h", self.fp.read(2))[0]
        else:
            co_flags = 0

        # In recording the address of co_code_offset_in file, skip
        # the type code indicator, e.g. "bytes" in 3.x and the size
        # of the string.
        co_code_offset_in_file = self.fp.tell() + 5

        # FIXME: Check/verify that is true:
        bytes_for_s = self.version_triple > (3, 0)

        # bytes_for_code = self.version_triple >= (2, 0)
        bytes_for_code = True
        co_code = self.r_object(bytes_for_s=bytes_for_code)

        co_consts = self.r_object(bytes_for_s=bytes_for_s)
        co_names = self.r_object(bytes_for_s=bytes_for_s)

        co_varnames = tuple()
        co_freevars = tuple()
        co_cellvars = tuple()

        if self.version_triple >= (3, 11) and not self.is_pypy:
            # parse localsplusnames list: https://github.com/python/cpython/blob/3.11/Objects/codeobject.c#L208C12
            co_localsplusnames = self.r_object(bytes_for_s=bytes_for_s)
            co_localspluskinds = self.r_object(bytes_for_s=bytes_for_s)

            CO_FAST_LOCAL = 0x20
            CO_FAST_CELL = 0x40
            CO_FAST_FREE = 0x80

            for name, kind in zip(co_localsplusnames, co_localspluskinds):
                if kind & CO_FAST_LOCAL:
                    co_varnames += (name,)
                    if kind & CO_FAST_CELL:
                        co_cellvars += (name,)
                elif kind & CO_FAST_CELL:
                    co_cellvars += (name,)
                elif kind & CO_FAST_FREE:
                    co_freevars += (name,)

            co_nlocals = len(co_varnames)
            co_filename = self.r_object(bytes_for_s=bytes_for_s)
            co_name = self.r_object(bytes_for_s=bytes_for_s)
            co_qualname = self.r_object(bytes_for_s=bytes_for_s)
            pass
        else:
            co_qualname = None
            if self.version_triple >= (1, 3):
                co_varnames = self.r_object(bytes_for_s=False)
            else:
                co_varnames = tuple()

            if self.version_triple >= (2, 0):
                co_cellvars = self.r_object(bytes_for_s=bytes_for_s)
                co_freevars = self.r_object(bytes_for_s=bytes_for_s)

            co_filename = self.r_object(bytes_for_s=bytes_for_s)
            co_name = self.r_object(bytes_for_s=bytes_for_s)
            if self.version_triple >= (3, 11) and self.is_pypy:
                co_qualname = self.r_object(bytes_for_s=bytes_for_s)

        co_exceptiontable = None

        if self.version_triple >= (1, 5):
            if self.version_triple >= (2, 3):
                co_firstlineno = unpack("<i", self.fp.read(4))[0]
            else:
                co_firstlineno = unpack("<h", self.fp.read(2))[0]

            if self.version_triple >= (3, 11) and not self.is_pypy:
                co_linetable = self.r_object(bytes_for_s=bytes_for_s)
                co_lnotab = (
                    co_linetable  # will be parsed later in opcode.findlinestarts
                )
                co_exceptiontable = self.r_object(bytes_for_s=bytes_for_s)
            else:
                co_lnotab = self.r_object(bytes_for_s=bytes_for_s)
        else:
            # < 1.5 there is no lnotab, so no firstlineno.
            # SET_LINENO is used instead.
            co_firstlineno = -1  # Bogus sentinel value
            co_lnotab = b""

        reference_objects = set(self.intern_objects + self.intern_strings)

        code = to_portable(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=kwonlyargcount,
            co_nlocals=co_nlocals,
            co_stacksize=co_stacksize,
            co_flags=co_flags,
            co_code=co_code,
            co_consts=co_consts,
            co_names=co_names,
            co_varnames=co_varnames,
            co_filename=co_filename,
            co_name=co_name,
            co_qualname=co_qualname,
            co_firstlineno=co_firstlineno,
            co_lnotab=co_lnotab,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_exceptiontable=co_exceptiontable,
            version_triple=self.version_triple,
            collection_order=self.collection_order,
            reference_objects=reference_objects,
        )

        self.code_to_file_offsets[code] = (code_offset_in_file, co_code_offset_in_file)

        self.code_objects[str(code)] = code
        ret = code

        return self.r_ref_insert(ret, i)

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

    def t_code_old(self, _, bytes_for_s: bool = False):
        """
        Python code type in all of its horrific variations.
        """

        # Go back one byte to TYPE_CODE "C"
        code_offset_in_file = self.fp.tell() - 1

        # Below, the value None (slot for a code object value), will
        # be replaced by the actual code in variable `ret` after it
        # has been built.
        ret, i = self.r_ref_reserve(None, False)

        self.version_triple = magic_int2tuple(self.magic_int)

        co_argcount = 0
        co_posonlyargcount = None
        kwonlyargcount = 0

        co_nlocals = 0
        co_stacksize = 0
        co_flags = 0

        # In recording the address of co_code_offset_in file, skip
        # the type code indicator, e.g. "bytes" in 3.x and the size
        # of the string.
        co_code_offset_in_file = self.fp.tell() + 5

        # FIXME: Check/verify that is true:
        bytes_for_code = True
        co_code = self.r_object(bytes_for_s=bytes_for_code)

        co_consts = self.r_object(bytes_for_s=bytes_for_s)
        co_names = self.r_object(bytes_for_s=bytes_for_s)

        co_varnames = tuple()
        co_freevars = tuple()
        co_cellvars = tuple()

        co_qualname = None
        if self.version_triple >= (1, 3):
            co_varnames = self.r_object(bytes_for_s=False)
        else:
            co_varnames = tuple()

        if self.version_triple >= (2, 0):
            co_freevars = self.r_object(bytes_for_s=bytes_for_s)
            co_cellvars = self.r_object(bytes_for_s=bytes_for_s)

        co_filename = self.r_object(bytes_for_s=bytes_for_s)
        co_name = self.r_object(bytes_for_s=bytes_for_s)
        if self.version_triple >= (3, 11) and self.is_pypy:
            co_qualname = self.r_object(bytes_for_s=bytes_for_s)

        co_exceptiontable = None

        # < 1.5 there is no lnotab, so no firstlineno.
        # SET_LINENO is used instead.
        co_firstlineno = -1  # Bogus sentinel value
        co_lnotab = b""

        reference_objects = set(self.intern_objects + self.intern_strings)

        code = to_portable(
            co_argcount=co_argcount,
            co_posonlyargcount=co_posonlyargcount,
            co_kwonlyargcount=kwonlyargcount,
            co_nlocals=co_nlocals,
            co_stacksize=co_stacksize,
            co_flags=co_flags,
            co_code=co_code,
            co_consts=co_consts,
            co_names=co_names,
            co_varnames=co_varnames,
            co_filename=co_filename,
            co_name=co_name,
            co_qualname=co_qualname,
            co_firstlineno=co_firstlineno,
            co_lnotab=co_lnotab,
            co_freevars=co_freevars,
            co_cellvars=co_cellvars,
            co_exceptiontable=co_exceptiontable,
            version_triple=self.version_triple,
            collection_order=self.collection_order,
            reference_objects=reference_objects,
        )

        self.code_to_file_offsets[code] = (code_offset_in_file, co_code_offset_in_file)

        self.code_objects[str(code)] = code
        ret = code

        return self.r_ref_insert(ret, i)

    def t_code_old_or_graal(self, save_ref, bytes_for_s: bool = False):
        """
        Python code type in all of its horrific variations.
        """
        if self.is_graal:
            return self.t_code_graal(save_ref, bytes_for_s)
        else:
            return self.t_code_old(save_ref, bytes_for_s)

    def t_graal_CodeUnit(self, save_ref, bytes_for_s: bool = False):
        """
        Graal Python code. This has fewer fields than Python
        code. In particular, instructions are JVM bytecode.
        """

        graal_bytecode_version = self.graal_readByte()
        assert (21000 + graal_bytecode_version * 10) in GRAAL3_MAGICS
        if graal_bytecode_version in (26,):
            self.version_triple = (3, 8, 5)

        other_fields: Dict = {}

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
        co_argcount = self.graal_readInt()
        co_kwonlyargcount = self.graal_readInt()
        co_posonlyargcount = self.graal_readInt()

        co_stacksize = self.graal_readInt()
        co_code_offset_in_file = self.fp.tell()
        co_code = self.graal_readBytes()
        other_fields["srcOffsetTable"] = self.graal_readBytes()
        co_flags = self.graal_readInt()

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
        other_fields["condition_profileCount"] = self.graal_readInt()
        other_fields["startLine"] = self.graal_readInt()
        other_fields["startColumn"] = self.graal_readInt()
        other_fields["endLine"] = self.graal_readInt()
        other_fields["endColumn"] = self.graal_readInt()
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

    # Since Python 3.4
    def t_object_reference(self, save_ref=None, bytes_for_s: bool = False):
        refnum = unpack("<i", self.fp.read(4))[0]
        return self.intern_objects[refnum]

    def t_unknown(self, save_ref=None, bytes_for_s: bool = False):
        raise KeyError("?")


# _________________________________________________________________
#
# user interface


def load_code(fp, magic_int, bytes_for_s: bool = False, code_objects={}):
    if isinstance(fp, bytes):
        fp = io.BytesIO(fp)
    um_gen = _VersionIndependentUnmarshaller(
        fp, magic_int, bytes_for_s, code_objects=code_objects
    )
    return um_gen.load()


def load_code_and_get_file_offsets(
    fp, magic_int, bytes_for_s: bool = False, code_objects={}
) -> tuple:
    if isinstance(fp, bytes):
        fp = io.BytesIO(fp)
    um_gen = _VersionIndependentUnmarshaller(
        fp, magic_int, bytes_for_s, code_objects=code_objects
    )
    return um_gen.load(), um_gen.code_to_file_offsets
