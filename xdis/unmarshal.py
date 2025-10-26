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
import sys
from struct import unpack

from xdis.codetype import to_portable
from xdis.cross_types import LongTypeForPython3, UnicodeForPython3
from xdis.magics import GRAAL3_MAGICS, PYPY3_MAGICS, RUSTPYTHON_MAGICS, magic_int2tuple
from xdis.version_info import version_tuple_to_str


def long(n: int) -> LongTypeForPython3:
    return LongTypeForPython3(n)

    # FIXME: we should write a bytes() class with a repr
    # that prints the b'' prefix so that Python2 can
    # print out Python3 code correctly


# Bit set on marshalType if we should
# add obj to internObjects.
# FLAG_REF is the marshal.c name
FLAG_REF = 0x80

TYPE_ASCII = "a"  # since 3.4
TYPE_ASCII_INTERNED = "A"  # since 3.4
TYPE_BINARY_COMPLEX = "y"  # 3.x
TYPE_BINARY_FLOAT = "g"
TYPE_CODE = "c"
TYPE_CODE_OLD = "C"  # used in Python 1.0 - 1.2
TYPE_COMPLEX = "x"
TYPE_DICT = "{"
TYPE_ELLIPSIS = "."
TYPE_FALSE = "F"
TYPE_FLOAT = "f"  # Seems not in use after Python 2.4
TYPE_FROZENSET = ">"
TYPE_INT = "i"
TYPE_INT64 = "I"  # Python 3.4 removed this
TYPE_INTERNED = "t"
TYPE_LIST = "["
TYPE_LONG = "l"
TYPE_NONE = "N"
TYPE_NULL = "0"
TYPE_REF = "r"  # Since 3.4
TYPE_SET = "<"
TYPE_SHORT_ASCII = "z"  # since 3.4
TYPE_SHORT_ASCII_INTERNED = "Z"  # since 3.4
TYPE_SMALL_TUPLE = ")"  # since 3.4
TYPE_STOPITER = "S"
TYPE_STRING = "s"
TYPE_STRINGREF = "R"  # Python 2
TYPE_TRUE = "T"
TYPE_TUPLE = "("
TYPE_UNICODE = "u"
TYPE_UNKNOWN = "?"

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
    TYPE_CODE: "code",
    TYPE_CODE_OLD: "code",  # Older Python code
    TYPE_COMPLEX: "complex",
    TYPE_DICT: "dict",
    TYPE_ELLIPSIS: "Ellipsis",
    TYPE_FALSE: "False",
    TYPE_FLOAT: "float",
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
    TYPE_SMALL_TUPLE: "small_tuple",
    TYPE_STOPITER: "stopIteration",
    TYPE_STRING: "string",
    TYPE_STRINGREF: "python2_string_reference",
    TYPE_TRUE: "True",
    TYPE_TUPLE: "tuple",
    TYPE_UNICODE: "unicode",
    TYPE_UNKNOWN: "unknown",
}


def compat_str(s):
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
            4: [3.4a3, current) (self.magic_int: 3280 onwards)

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
        version = magic_int2tuple(self.magic_int)
        if version >= (3, 4):
            if self.magic_int in (3250, 3260, 3270):
                self.marshal_version = 3
            else:
                self.marshal_version = 4
        elif (3, 4) > version >= (2, 5):
            self.marshal_version = 2
        elif (2, 5) > version >= (2, 4):
            self.marshal_version = 1
        else:
            self.marshal_version = 0

        self.internStrings = []
        self.internObjects = []
        self.version_tuple = tuple()
        self.is_graal = magic_int in GRAAL3_MAGICS
        self.is_pypy = magic_int in PYPY3_MAGICS
        self.is_rust = magic_int in RUSTPYTHON_MAGICS

        if magic_int in RUSTPYTHON_MAGICS:
            raise NotImplementedError(
                "RustPython %s is not supported yet." % version_tuple_to_str(version)
            )

    def load(self):
        """
        ``marshal.load()`` written in Python. When the Python bytecode magic loaded is the
        same magic for the running Python interpreter, we can simply use the
        Python-supplied marshal.load().

        However, we need to use this when versions are different since the internal
        code structures are different. Sigh.
        """

        if self.marshal_version == 0:
            self.internStrings = []
        if self.marshal_version < 3:
            assert self.internObjects == []

        return self.r_object()

    # Python 3.4+ support for reference objects.
    # The names follow marshal.c
    def r_ref_reserve(self, obj, save_ref):
        i = None
        if save_ref:
            i = len(self.internObjects)
            self.internObjects.append(obj)
        return obj, i

    def r_ref_insert(self, obj, i):
        if i is not None:
            self.internObjects[i] = obj
        return obj

    def r_ref(self, obj, save_ref):
        if save_ref:
            self.internObjects.append(obj)
        return obj

    # In marshal.c this is one big case statement
    # FIXME: remove bytes_fo_s parameter.
    # Now that we have git branches, isolated by Python version.
    # This is only needed in the Python 2.4 - 2.7 code branch.
    def r_object(self, bytes_for_s: bool = False):
        """
        Main object unmarshalling read routine.  Reads from self.fp
        the next byte which is a key in UNMARSHAL_DISPATCH_TABLE
        defined above when the high-order bit, FLAG_REF is not set.
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

    def t_stopIteration(self, save_ref, bytes_for_s: bool = False):
        return StopIteration

    def t_Ellipsis(self, save_ref, bytes_for_s: bool = False):
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
            self.internObjects.append(obj)
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

    # Note: could mean bytes in Python3 processing Python2 bytecode
    def t_string(self, save_ref, bytes_for_s):
        """
        In Python3, this is a ``bytes`` type.  In Python2, it is a string type;
        ``bytes_for_s`` distinguishes what we need.
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
        self.internStrings.append(interned)
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
        self.internStrings.append(interned)
        return self.r_ref(interned, save_ref)

    # Since Python 3.4
    def t_interned(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("<i", self.fp.read(4))[0]
        interned = compat_str(self.fp.read(strsize))
        self.internStrings.append(interned)
        return self.r_ref(interned, save_ref)

    def t_unicode(self, save_ref, bytes_for_s: bool = False):
        strsize = unpack("<i", self.fp.read(4))[0]
        unicodestring = self.fp.read(strsize)
        if self.version_tuple < (3, 0):
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
        return self.internStrings[refnum]

    def t_code(self, save_ref, bytes_for_s: bool = False):
        """
        Python code type in all of its horrific variations.
        """
        # FIXME: use tables to simplify this?
        # FIXME: Python 1.0 .. 1.3 isn't well known

        # Go back one byte to TYPE_CODE "c" or "c" with the FLAG_REF
        # set.
        code_offset_in_file = self.fp.tell() - 1

        ret, i = self.r_ref_reserve(None, save_ref)
        self.version_tuple = magic_int2tuple(self.magic_int)

        if self.version_tuple >= (2, 3):
            co_argcount = unpack("<i", self.fp.read(4))[0]
        elif self.version_tuple >= (1, 3):
            co_argcount = unpack("<h", self.fp.read(2))[0]
        else:
            co_argcount = 0

        if self.version_tuple >= (3, 8):
            co_posonlyargcount = (
                0
                if self.magic_int in (3400, 3401, 3410, 3411)
                else unpack("<i", self.fp.read(4))[0]
            )
        else:
            co_posonlyargcount = None

        if self.version_tuple >= (3, 0):
            kwonlyargcount = unpack("<i", self.fp.read(4))[0]
        else:
            kwonlyargcount = 0

        co_nlocals = 0
        if self.version_tuple < (3, 11) or (
            self.version_tuple[:2] == (3, 11) and self.is_pypy
        ):
            if self.version_tuple >= (2, 3):
                co_nlocals = unpack("<i", self.fp.read(4))[0]
            elif self.version_tuple >= (1, 3):
                co_nlocals = unpack("<h", self.fp.read(2))[0]

        if self.version_tuple >= (2, 3):
            co_stacksize = unpack("<i", self.fp.read(4))[0]
        elif self.version_tuple >= (1, 5):
            co_stacksize = unpack("<h", self.fp.read(2))[0]
        else:
            co_stacksize = 0

        if self.version_tuple >= (2, 3):
            co_flags = unpack("<i", self.fp.read(4))[0]
        elif self.version_tuple >= (1, 3):
            co_flags = unpack("<h", self.fp.read(2))[0]
        else:
            co_flags = 0

        # In recording the address of co_code_offset_in file, skip
        # the type code indicator, e.g. "bytes" in 3.x and the size
        # of the string.
        co_code_offset_in_file = self.fp.tell() + 5

        # bytes_for_code = self.version_tuple >= (2, 0)
        bytes_for_code = True
        co_code = self.r_object(bytes_for_s=bytes_for_code)

        # FIXME: Check/verify that is true:
        bytes_for_s = self.version_tuple > (3, 0)
        if self.is_graal:
            co_consts = tuple()
            co_names = tuple()
            code = to_portable(
                co_argcount=0,
                co_posonlyargcount=0,
                co_kwonlyargcount=0,
                co_nlocals=0,
                co_stacksize=0,
                co_flags=0,
                co_code=co_code,
                co_consts=tuple(),
                co_names=tuple(),
                co_varnames=tuple(),
                co_filename="??",
                co_name="??",
                co_qualname="??",
                co_firstlineno=0,
                co_lnotab="",
                co_freevars=tuple(),
                co_cellvars=tuple(),
                co_exceptiontable=None,
                version_triple=self.version_tuple,
            )
            ret = code
            return self.r_ref_insert(ret, i)

        co_consts = self.r_object(bytes_for_s=bytes_for_s)
        co_names = self.r_object(bytes_for_s=bytes_for_s)

        co_varnames = tuple()
        co_freevars = tuple()
        co_cellvars = tuple()

        if self.version_tuple >= (3, 11) and not self.is_pypy:
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
            if self.version_tuple >= (1, 3):
                co_varnames = self.r_object(bytes_for_s=False)
            else:
                co_varnames = tuple()

            if self.version_tuple >= (2, 0):
                co_freevars = self.r_object(bytes_for_s=bytes_for_s)
                co_cellvars = self.r_object(bytes_for_s=bytes_for_s)

            co_filename = self.r_object(bytes_for_s=bytes_for_s)
            co_name = self.r_object(bytes_for_s=bytes_for_s)
            if self.version_tuple >= (3, 11) and self.is_pypy:
                co_qualname = self.r_object(bytes_for_s=bytes_for_s)

        co_exceptiontable = None

        if self.version_tuple >= (1, 5):
            if self.version_tuple >= (2, 3):
                co_firstlineno = unpack("<i", self.fp.read(4))[0]
            else:
                co_firstlineno = unpack("<h", self.fp.read(2))[0]

            if self.version_tuple >= (3, 11) and not self.is_pypy:
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
            version_triple=self.version_tuple,
            collection_order=self.collection_order,
        )

        self.code_to_file_offsets[code] = (code_offset_in_file, co_code_offset_in_file)

        self.code_objects[str(code)] = code
        ret = code

        return self.r_ref_insert(ret, i)

    # Since Python 3.4
    def t_object_reference(self, save_ref=None, bytes_for_s: bool = False):
        refnum = unpack("<i", self.fp.read(4))[0]
        o = self.internObjects[refnum]
        return o

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
