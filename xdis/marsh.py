# (C) Copyright 2018-2025 by Rocky Bernstein
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

"""Internal Python object serialization

This module contains functions that can read and write Python values
in a binary format. The format is specific to Python, but independent
of machine architecture issues (e.g., you can write a Python value to
a file on a PC, transport the file to a Sun, and read it back
there). Details of the format may change between Python versions.

"""

import struct
import types
from sys import intern
from typing import Any, Dict, Optional, Set, Union

from xdis.codetype import Code2, Code3, Code15
from xdis.unmarshal import (
    FLAG_REF,
    TYPE_ASCII,
    TYPE_BINARY_COMPLEX,
    TYPE_BINARY_FLOAT,
    TYPE_CODE,
    TYPE_COMPLEX,
    TYPE_DICT,
    TYPE_ELLIPSIS,
    TYPE_FALSE,
    TYPE_FLOAT,
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
    TYPE_SMALL_TUPLE,
    TYPE_STOPITER,
    TYPE_STRING,
    TYPE_STRINGREF,
    TYPE_TRUE,
    TYPE_TUPLE,
    TYPE_UNICODE,
    long,
)
from xdis.version_info import PYTHON_VERSION_TRIPLE, version_tuple_to_str

# NOTE: This module is used in the Python3 interpreter, but also by
# the "sandboxed" process.  It must work for Python2 as well.

try:
    from __pypy__ import builtinify

except ImportError:

    def builtinify(f):
        return f


class _Marshaller:
    """Python marshalling routine that runs in Python 2 and Python 3.
    We also extend to allow for xdis Code15, Code2, and Code3 types and instances.
    """

    dispatch = {}

    def __init__(
        self,
        writefunc,
        python_version: tuple,
        is_pypy: Optional[bool] = None,
        collection_order={},
        reference_objects=set(),
    ) -> None:
        self._write = writefunc
        self.collection_order = collection_order
        self.intern_objects: Dict[Any, int] = {}
        self.intern_consts: Dict[Any, int] = {}
        self.is_pypy = is_pypy
        self.python_version = python_version
        self.reference_objects = reference_objects

    def dump(self, x, flag_ref: int = 0) -> None:
        if (
            isinstance(x, types.CodeType)
            and PYTHON_VERSION_TRIPLE[:2] != self.python_version[:2]
        ):
            raise RuntimeError(
                "code type passed for version %s but we are running version %s"
                % (version_tuple_to_str(), self.python_version)
            )
        try:
            self.dispatch[type(x)](self, x, flag_ref)
        except KeyError:
            if isinstance(x, Code3):
                self.dispatch[Code3](self, x)
                return
            elif isinstance(x, Code2):
                self.dispatch[Code2](self, x)
                return
            elif isinstance(x, Code15):
                self.dispatch[Code15](self, x)
                return
            else:
                for tp in type(x).mro():
                    func = self.dispatch.get(tp)
                    if func:
                        break
                else:
                    raise ValueError("unmarshallable object")
            func(self, x)

    # FIXME: Handle interned versions of dump_ascii, dump_short_ascii
    def dump_ascii(self, s: str) -> None:
        self._write(TYPE_ASCII)
        self.w_long(len(s))
        self._write(s)

    dispatch[TYPE_ASCII] = dump_ascii

    def dump_binary_complex(self, x) -> None:
        write = self._write
        write(TYPE_BINARY_COMPLEX)
        write(struct.pack("<d", x.real))
        write(struct.pack("<d", x.imag))

    dispatch[TYPE_BINARY_COMPLEX] = dump_binary_complex

    def dump_binary_float(self, x) -> None:
        write = self._write
        write(TYPE_BINARY_FLOAT)
        write(struct.pack("<d", x))

    def dump_bool(self, x) -> None:
        if x:
            self._write(TYPE_TRUE)
        else:
            self._write(TYPE_FALSE)

    dispatch[bool] = dump_bool

    def dump_code15(self, x) -> None:
        # Careful here: many Python 2 code objects are strings,
        # but Python 3 marshaling, by default, will dump strings as
        # unicode. Force marsaling this type as string.

        self._write(TYPE_CODE)
        self.w_short(x.co_argcount)
        self.w_short(x.co_nlocals)
        self.w_short(x.co_stacksize)
        self.w_short(x.co_flags)
        self.dump_string(x.co_code)

        # If running in a Python3 interpreter, some constants will get
        # converted from string to unicode. For now, let's see if
        # that's okay.
        self.dump(x.co_consts)

        # The tuple "names" in Python 1.x must have string entries
        self._write(TYPE_TUPLE)
        self.w_long(len(x.co_names))
        for name in x.co_names:
            self.dump_string(name)

        # The tuple "varnames" in Python 1.x also must have string entries
        self._write(TYPE_TUPLE)
        self.w_long(len(x.co_varnames))
        for name in x.co_varnames:
            self.dump_string(name)

        self.dump_string(x.co_filename)
        self.dump_string(x.co_name)
        self.w_long(x.co_firstlineno)
        self.dump_string(x.co_lnotab)
        return

    dispatch[Code15] = dump_code15

    def dump_code2(self, x, _) -> None:
        # Careful here: many Python 2 code objects are strings,
        # but Python 3 marshaling, by default, will dump strings as
        # unicode. Force marsaling this type as string.

        self._write(TYPE_CODE)
        self.w_long(x.co_argcount)
        self.w_long(x.co_nlocals)
        self.w_long(x.co_stacksize)
        self.w_long(x.co_flags)
        self.dump_string(x.co_code)

        # If running in a Python3 interpreter, some constants will get
        # converted from string to unicode. For now, let's see if
        # that's okay.
        self.dump(x.co_consts)

        # The tuple "names" in Python2 must have string entries
        self._write(TYPE_TUPLE)
        self.w_long(len(x.co_names))
        for name in x.co_names:
            self.dump_string(name)

        # The tuple "varnames" in Python2 also must have string entries
        self._write(TYPE_TUPLE)
        self.w_long(len(x.co_varnames))
        for name in x.co_varnames:
            self.dump_string(name)

        self.dump(x.co_freevars)
        self.dump(x.co_cellvars)
        self.dump_string(x.co_filename)
        self.dump_string(x.co_name)
        self.w_long(x.co_firstlineno)
        self.dump_string(x.co_lnotab)
        return

    dispatch[Code2] = dump_code2

    # FIXME: will probably have to adjust similar to how we
    # adjusted dump_code2
    def dump_code3(self, code, flag_ref: int = 0) -> None:
        if flag_ref:
            self._write(chr(ord(TYPE_CODE) | flag_ref))

            # The way marshal works for 3.4 (up to ....?)
            # The first object is always None. Supposedly that
            # object is to be filled in by the code at the end,
            # but by filling in "None" first, that gets used should
            # there be other instances of None. Seems like a bug,
            # but this is Python after all
            self.intern_consts[None] = 0

            # This is probably wrong. We are off by one in
            # intern_objects.
            self.intern_objects[code] = len(self.intern_objects)

        else:
            self._write(TYPE_CODE)

        self.w_long(code.co_argcount)
        if hasattr(code, "co_posonlyargcount"):
            self.w_long(code.co_posonlyargcount)
        self.w_long(code.co_kwonlyargcount)
        if self.python_version < (3, 11):
            self.w_long(code.co_nlocals)
        self.w_long(code.co_stacksize)
        self.w_long(code.co_flags)
        self.dump(code.co_code)
        self.dump(code.co_consts, flag_ref)
        self.dump_names(code.co_names, flag_ref)
        self.dump_names(code.co_varnames, flag_ref)
        self.dump_names(code.co_freevars, flag_ref)
        self.dump_names(code.co_cellvars, flag_ref)
        self.dump_filename(code.co_filename, flag_ref)
        self.dump_name(code.co_name, flag_ref)
        self.w_long(code.co_firstlineno)

        # 3.10 and greater uses co_linetable.
        linetable = code.co_linetable if hasattr(code, "co_linetable") else code.co_lnotab
        self.dump_linetable(linetable)

    dispatch[Code3] = dump_code3

    # FIXME: this is wrong.
    try:
        dispatch[types.CodeType] = dump_code3
    except NameError:
        pass

    def dump_collection(self, type_code: str, bag: Union[frozenset, set, dict]) -> None:
        """
        Save marshalled version of frozenset fs.
        Use self.collection_order, to ensure that the order
        or set elements that may have appeared from unmarshalling the appears
        the same way. This helps roundtrip checking, among possibly other things.
        """
        self._write(type_code)
        self.w_long(len(bag))
        collection = self.collection_order.get(bag, bag)
        for each in collection:
            self.dump(each)

    def dump_complex(self, x, _) -> None:
        write = self._write
        write(TYPE_COMPLEX)
        s = repr(x.real)
        write(chr(len(s)))
        write(s)
        s = repr(x.imag)
        write(chr(len(s)))
        write(s)

    try:
        dispatch[complex] = dump_complex
    except NameError:
        pass

    def dump_dict(self, x) -> None:
        self._write(TYPE_DICT)
        for key, value in x.items():
            self.dump(key)
            self.dump(value)
        self._write(TYPE_NULL)

    dispatch[dict] = dump_dict

    def dump_ellipsis(self, _) -> None:
        self._write(TYPE_ELLIPSIS)

    try:
        dispatch[type(Ellipsis)] = dump_ellipsis
    except NameError:
        pass

    def dump_float(self, x) -> None:
        write = self._write
        write(TYPE_FLOAT)
        s = repr(x)
        write(chr(len(s)))
        write(s)

    dispatch[float] = dump_float
    dispatch[TYPE_BINARY_FLOAT] = dump_float

    def dump_filename(self, path, flag_ref: int = 0) -> None:
        if flag_ref:
            # After Python 3.4 which adds the ref flag and ASCII marshal types..
            if len(path) < 256:
                self.dump_short_ascii(path)
            else:
                self.dump_ascii(path)
        else:
            # Python 3.0 .. 3.4...
            self.dump_unicode(path)

    def dump_frozenset(self, fs: frozenset, flag_ref: int = 0) -> None:
        """
        Save marshalled version of frozenset fs.
        """
        self.dump_collection(TYPE_FROZENSET, fs)

    try:
        dispatch[frozenset] = dump_frozenset
    except NameError:
        pass

    def dump_linetable(self, s) -> None:
        type_code = TYPE_STRING if self.python_version < (3, 5) else TYPE_UNICODE
        self._write(type_code)
        self.w_long(len(s))
        self._write(s)

    def w_long(self, x: int) -> None:
        a = chr(x & 0xFF)
        x >>= 8
        b = chr(x & 0xFF)
        x >>= 8
        c = chr(x & 0xFF)
        x >>= 8
        d = chr(x & 0xFF)
        self._write(a + b + c + d)

    def w_long64(self, x) -> None:
        self.w_long(x)
        self.w_long(x >> 32)

    def dump_name(self, name: str, flag_ref: int) -> None:
        if flag_ref:
            if len(name) < 256:
                self.dump_short_ascii_interned(name)
            else:
                self.dump_ascii(name)
        else:
            self.dump_unicode(name)


    def dump_names(self, names, flag_ref: int) -> None:
        n = len(names)
        if flag_ref:

            # We have reference objects. Has "names" already been seen as a reference object?
            if names in self.intern_objects:
                # It has, so just write the reference and return.
                self._write(TYPE_REF)
                self.w_long(self.intern_objects[names])
                return

            if n < 256:
                is_reference = names in self.reference_objects
                type_code = (
                    chr(ord(TYPE_SMALL_TUPLE) | FLAG_REF)
                    if is_reference
                    else TYPE_SMALL_TUPLE
                )
                self._write(type_code)
                self._write(chr(n))
                if is_reference:
                    self.intern_objects[names] = len(self.intern_objects)

            else:
                self._write(chr(ord(TYPE_TUPLE) | FLAG_REF))
                self.w_long(n)

            for name in names:
                self.dump_short_ascii_interned(name)
        else:
            self._write(TYPE_TUPLE)
            self.w_long(n)
            for name in names:
                self.dump(name)

    def dump_none(self, _, flag_ref: int) -> None:
        self._write(TYPE_NONE)
        # In Python 3.4 .. ? None appears always as the first
        # constant.
        if flag_ref and self.intern_consts.get(None, -1) == -1:
            self.intern_consts[None] = len(self.intern_consts)

    dispatch[type(None)] = dump_none

    def dump_int(self, value: int, flag_ref: int = 0) -> None:
        if flag_ref:
            ref = self.intern_consts.get(value, None)
            if ref is not None:
                self.dump_ref(ref)
                return
            n = len(self.intern_consts)
            self.intern_consts[value] = n

        y = value >> 31
        if y and y != -1:
            self._write(chr(ord(TYPE_INT64) | flag_ref))
            self.w_long64(value)
        else:
            self._write(chr(ord(TYPE_INT) | flag_ref))
            self.w_long(value)

    dispatch[int] = dump_int

    def dump_list(self, x) -> None:
        self._write(TYPE_LIST)
        self.w_long(len(x))
        for item in x:
            self.dump(item)

    dispatch[list] = dump_list

    def dump_long(self, x) -> None:
        self._write(TYPE_LONG)
        sign = 1
        if x < 0:
            sign = -1
            x = -x
        digits = []
        while x:
            digits.append(x & 0x7FFF)
            x = x >> 15
        self.w_long(len(digits) * sign)
        for d in digits:
            self.w_short(d)

    try:
        long
    except NameError:
        dispatch[int] = dump_long
    else:
        dispatch[long] = dump_long  # noqa

    def dump_ref(self, ref: int) -> None:
        self._write(TYPE_REF)
        self.w_long(ref)

    def dump_set(self, s: set) -> None:
        """
        Save marshalled version of set s.
        """
        self.dump_collection(TYPE_SET, s)

    dispatch[set] = dump_set

    def w_short(self, x: int) -> None:
        self._write(chr(x & 0xFF))
        self._write(chr((x >> 8) & 0xFF))

    def dump_short_ascii(self, short_ascii: str) -> None:
        self._write(chr(ord(TYPE_SHORT_ASCII) | FLAG_REF))
        # FIXME: check len(x)?
        self._write(chr(len(short_ascii)))
        self._write(short_ascii)

    dispatch[TYPE_SHORT_ASCII] = dump_short_ascii

    def dump_short_ascii_interned(self, short_ascii: str) -> None:
        """
        Used when the length of an ASCII string is less than 255
        characters. This is used in Python 3.4 and later.
        """
        ref = self.intern_consts.get(short_ascii, None)
        if ref is not None:
            self.dump_ref(ref)
            return

        self._write(chr(ord(TYPE_SHORT_ASCII_INTERNED) | FLAG_REF))
        self._write(chr(len(short_ascii)))
        self._write(short_ascii)
        n = len(self.intern_objects)
        self.intern_objects[short_ascii] = n

    dispatch[TYPE_ASCII] = dump_ascii

    def dump_small_tuple(self, tuple_value, flag_ref: int) -> None:
        """
        Used when the length of a tuple has is less than 255
        items. This is used in Python 3.4 and later.
        """
        if flag_ref:
            ref = self.intern_objects.get(tuple_value, None)
            if ref is not None:
                self.dump_ref(ref)
                return
            n = len(self.intern_objects)
            self.intern_objects[tuple_value] = n

        self._write(TYPE_SMALL_TUPLE)
        self._write(chr(len(tuple_value)))
        for item in tuple_value:
            self.dump(item, FLAG_REF)

    dispatch[TYPE_SMALL_TUPLE] = dump_small_tuple

    def dump_stopiter(self, x) -> None:
        if x is not StopIteration:
            raise ValueError("unmarshallable object")
        self._write(TYPE_STOPITER)

    dispatch[type(StopIteration)] = dump_stopiter

    def dump_string(self, s, flag_ref: int = 0) -> None:
        # Python 3.11 seems to add the object ref flag bit for strings.
        if self.python_version >= (3, 11):
            type_code = chr(ord(TYPE_STRING) | flag_ref)
        if (3, 0) <= self.python_version < (3, 11):
            type_code = TYPE_STRING
        else:
            # Python 2.x.
            # FIXME: save string somewhere if it isn't in string table.
            type_code = TYPE_INTERNED if s in self.reference_objects else TYPE_STRING

        self._write(type_code)
        self.w_long(len(s))
        self._write(s)

    dispatch[bytes] = dump_string
    dispatch[bytearray] = dump_string

    def dump_tuple(self, tuple_object: tuple, flag_ref: int = 0) -> None:

        n = len(tuple_object)
        if self.python_version >= (3, 4) and n < 256:
            self.dump_small_tuple(tuple_object, flag_ref)
            return

        type_code = TYPE_TUPLE
        self._write(type_code)
        self.w_long(len(tuple_object))
        for item in tuple_object:
            self.dump(item)

    dispatch[tuple] = dump_tuple
    dispatch[TYPE_TUPLE] = dump_tuple
    dispatch[TYPE_LIST] = dump_tuple

    def dump_unicode(self, s, flag_ref: int = 0) -> None:
        if self.python_version < (2, 0):
            type_code = TYPE_STRING
        elif (2, 0) <= self.python_version < (3, 0):
            # FIXME: probably need to save string somewhere
            # if it isn't in string table.
            type_code = TYPE_INTERNED if s in self.reference_objects else TYPE_STRING
        else:
            type_code = TYPE_UNICODE

        if flag_ref:
            ref = self.intern_objects.get(s, None)
            if ref is not None:
                self.dump_ref(ref)
                return
            n = len(self.intern_objects)
            self.intern_objects[s] = n
            type_code = chr(ord(type_code) | flag_ref)

        self._write(type_code)
        self.w_long(len(s))
        self._write(s)

    try:
        unicode
    except NameError:
        dispatch[str] = dump_unicode
    else:
        dispatch[unicode] = dump_unicode  # noqa



class _NULL:
    pass


class _StringBuffer:
    def __init__(self, value) -> None:
        self.bufstr = value
        self.bufpos = 0

    def read(self, n):
        pos = self.bufpos
        newpos = pos + n
        ret = self.bufstr[pos:newpos]
        self.bufpos = newpos
        return ret


class _Unmarshaller:
    dispatch = {}

    def __init__(self, readfunc, python_version: bool, is_pypy: bool) -> None:
        self._read = readfunc
        self._stringtable = []
        self.is_pypy = is_pypy
        self.python_version = python_version

    def load(self):
        c = self._read(1)
        if not c:
            raise EOFError
        try:
            return self.dispatch[c](self)
        except KeyError:
            raise ValueError("bad marshal code: %c (%d)" % (c, c))

    def r_byte(self):
        return self._read(1)

    def r_long(self):
        s = self._read(4)
        a = s[0]
        b = s[1]
        c = s[2]
        d = s[3]
        x = a | (b << 8) | (c << 16) | (d << 24)
        if d & 0x80 and x > 0:
            x = -((1 << 32) - x)
            return int(x)
        else:
            return x

    dispatch[TYPE_INT] = r_long

    def r_long64(self):
        a = self._read(1)
        b = self._read(1)
        c = self._read(1)
        d = self._read(1)
        e = self._read(1)
        f = self._read(1)
        g = self._read(1)
        h = self._read(1)
        x = a | (b << 8) | (c << 16) | (d << 24)
        x = x | (e << 32) | (f << 40) | (g << 48) | (h << 56)
        if h & 0x80 and x > 0:
            x = -((1 << 64) - x)
        return x

    dispatch[TYPE_INT64] = r_long64

    def r_short(self):
        lo = self._read(1)
        hi = self._read(1)
        x = lo | (hi << 8)
        if x & 0x8000:
            x = x - 0x10000
        return x

    def load_null(self):
        return _NULL

    dispatch[TYPE_NULL] = load_null

    def load_ascii(self):
        return self.r_byte()

    dispatch[TYPE_ASCII] = load_ascii

    def load_binary_float(self) -> float:
        f = self._read(8)
        return float(struct.unpack("<d", f)[0])

    dispatch[TYPE_BINARY_FLOAT] = load_binary_float

    # FIXME: GO over fo PYPY
    def load_code(self) -> Code2 | Code3 | CodeType:
        argcount = self.r_long()
        if self.python_version and self.python_version >= (3, 0):
            is_python3 = True
            kwonlyargcount = self.r_long()
        else:
            is_python3 = False
        nlocals = self.r_long()
        stacksize = self.r_long()
        flags = self.r_long()
        code = self.load()
        consts = self.load()
        names = self.load()
        varnames = self.load()
        freevars = self.load()
        cellvars = self.load()
        filename = self.load()
        name = self.load()
        firstlineno = self.r_long()
        lnotab = self.load()
        if is_python3:
            return types.CodeType(
                argcount,
                kwonlyargcount,
                nlocals,
                stacksize,
                flags,
                code,
                consts,
                names,
                varnames,
                filename,
                name,
                firstlineno,
                lnotab,
                freevars,
                cellvars,
            )
        else:
            return Code2(
                argcount,
                nlocals,
                stacksize,
                flags,
                code,
                consts,
                names,
                varnames,
                filename,
                name,
                firstlineno,
                lnotab,
                freevars,
                cellvars,
            )

    dispatch[TYPE_CODE] = load_code

    def load_complex(self) -> complex:
        n = self._read(1)
        s = self._read(n)
        real = float(s)
        n = self._read(1)
        s = self._read(n)
        imag = float(s)
        return complex(real, imag)

    dispatch[TYPE_COMPLEX] = load_complex

    def load_dict(self):
        d = {}
        while 1:
            key = self.load()
            if key is _NULL:
                break
            value = self.load()
            d[key] = value
        return d

    dispatch[TYPE_DICT] = load_dict

    def load_ellipsis(self) -> EllipsisType:
        return Ellipsis

    dispatch[TYPE_ELLIPSIS] = load_ellipsis

    def load_false(self) -> bool:
        return False

    dispatch[TYPE_FALSE] = load_false

    def load_float(self) -> float:
        n = self._read(1)
        s = self._read(n)
        return float(s)

    dispatch[TYPE_FLOAT] = load_float

    def load_frozenset(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return frozenset(args)

    dispatch[TYPE_FROZENSET] = load_frozenset

    def load_interned(self) -> str:
        n = self.r_long()
        ret = intern(self._read(n))
        self._stringtable.append(ret)
        return ret

    dispatch[TYPE_INTERNED] = load_interned

    def load_list(self):
        n = self.r_long()
        list = [self.load() for i in range(n)]
        return list

    dispatch[TYPE_LIST] = load_list

    def load_long(self):
        size = self.r_long()
        sign = 1
        if size < 0:
            sign = -1
            size = -size
        x = 0
        for i in range(size):
            d = self.r_short()
            x = x | (d << (i * 15))
        return x * sign

    dispatch[TYPE_LONG] = load_long

    def load_none(self) -> None:
        return None

    dispatch[TYPE_NONE] = load_none

    def load_set(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return set(args)

    dispatch[TYPE_SET] = load_set

    def load_stopiter(self) -> type[StopIteration]:
        return StopIteration

    dispatch[TYPE_STOPITER] = load_stopiter

    def load_string(self):
        n = self.r_long()
        return self._read(n)

    dispatch[TYPE_STRING] = load_string

    def load_stringref(self):
        n = self.r_long()
        return self._stringtable[n]

    dispatch[TYPE_STRINGREF] = load_stringref

    def load_true(self) -> bool:
        return True

    dispatch[TYPE_TRUE] = load_true

    def load_tuple(self):
        return tuple(self.load_list())

    dispatch[TYPE_TUPLE] = load_tuple

    def load_unicode(self):
        n = self.r_long()
        s = self._read(n)
        ret = s.decode("utf8")
        return ret

    dispatch[TYPE_UNICODE] = load_unicode


# ________________________________________________________________


def _read(self, n):
    pos = self.bufpos
    newpos = pos + n
    if newpos > len(self.bufstr):
        raise EOFError
    ret = self.bufstr[pos:newpos]
    self.bufpos = newpos
    return ret


def _read1(self):
    ret = self.bufstr[self.bufpos]
    self.bufpos += 1
    return ret


def _r_short(self):
    lo = _read1(self)
    hi = _read1(self)
    x = lo | (hi << 8)
    if x & 0x8000:
        x = x - 0x10000
    return x


def _r_long(self):
    # inlined this most common case
    p = self.bufpos
    s = self.bufstr
    a = s[p]
    b = s[p + 1]
    c = s[p + 2]
    d = s[p + 3]
    self.bufpos += 4
    x = a | (b << 8) | (c << 16) | (d << 24)
    if d & 0x80 and x > 0:
        x = -((1 << 32) - x)
        return int(x)
    else:
        return x


def _r_long64(self):
    a = _read1(self)
    b = _read1(self)
    c = _read1(self)
    d = _read1(self)
    e = _read1(self)
    f = _read1(self)
    g = _read1(self)
    h = _read1(self)
    x = a | (b << 8) | (c << 16) | (d << 24)
    x = x | (e << 32) | (f << 40) | (g << 48) | (h << 56)
    if h & 0x80 and x > 0:
        x = -((1 << 64) - x)
    return x


_load_dispatch = {}


class _FastUnmarshaller:
    dispatch = {}

    def __init__(self, buffer, python_version=None) -> None:
        self.bufstr = buffer
        self.bufpos = 0
        self._stringtable = []
        self.python_version = python_version

    def load(self):
        # make flow space happy
        c = "?"
        try:
            c = self.bufstr[self.bufpos]
            c = chr(c)
            self.bufpos += 1
            return _load_dispatch[c](self)
        except KeyError:
            exception = ValueError(
                "bad marshal code at position %d: %c" % (self.bufpos - 1, c)
            )
        except IndexError:
            exception = EOFError
        raise exception

    def load_null(self):
        return _NULL

    dispatch[TYPE_NULL] = load_null

    def load_none(self) -> None:
        return None

    dispatch[TYPE_NONE] = load_none

    def load_true(self) -> bool:
        return True

    dispatch[TYPE_TRUE] = load_true

    def load_false(self) -> bool:
        return False

    dispatch[TYPE_FALSE] = load_false

    def load_stopiter(self):
        return StopIteration

    dispatch[TYPE_STOPITER] = load_stopiter

    def load_ellipsis(self):
        return Ellipsis

    dispatch[TYPE_ELLIPSIS] = load_ellipsis

    def load_int(self):
        return _r_long(self)

    dispatch[TYPE_INT] = load_int

    def load_int64(self):
        return _r_long64(self)

    dispatch[TYPE_INT64] = load_int64

    def load_long(self):
        size = _r_long(self)
        sign = 1
        if size < 0:
            sign = -1
            size = -size
        x = 0
        for i in range(size):
            d = _r_short(self)
            x = x | (d << (i * 15))
        return x * sign

    dispatch[TYPE_LONG] = load_long

    def load_float(self) -> float:
        n = _read1(self)
        s = _read(self, n)
        return float(s)

    dispatch[TYPE_FLOAT] = load_float

    def load_complex(self) -> complex:
        n = _read1(self)
        s = _read(self, n)
        real = float(s)
        n = _read1(self)
        s = _read(self, n)
        imag = float(s)
        return complex(real, imag)

    dispatch[TYPE_COMPLEX] = load_complex

    def load_string(self):
        n = _r_long(self)
        return _read(self, n)

    dispatch[TYPE_STRING] = load_string

    def load_interned(self) -> str:
        n = _r_long(self)
        s = _read(self, n)
        s = s.decode("utf8")
        ret = intern(s)
        self._stringtable.append(ret)
        return ret

    dispatch[TYPE_INTERNED] = load_interned

    def load_stringref(self):
        n = _r_long(self)
        return self._stringtable[n]

    dispatch[TYPE_STRINGREF] = load_stringref

    def load_unicode(self):
        n = _r_long(self)
        s = _read(self, n)
        ret = s.decode("utf8")
        return ret

    dispatch[TYPE_UNICODE] = load_unicode

    def load_tuple(self):
        return tuple(self.load_list())

    dispatch[TYPE_TUPLE] = load_tuple

    def load_list(self):
        n = _r_long(self)
        list = []
        for i in range(n):
            list.append(self.load())
        return list

    dispatch[TYPE_LIST] = load_list

    def load_dict(self):
        d = {}
        while 1:
            key = self.load()
            if key is _NULL:
                break
            value = self.load()
            d[key] = value
        return d

    dispatch[TYPE_DICT] = load_dict

    def load_code(self):
        argcount = _r_long(self)
        nlocals = _r_long(self)
        stacksize = _r_long(self)
        flags = _r_long(self)
        code = self.load()
        consts = self.load()
        names = self.load()
        varnames = self.load()
        freevars = self.load()
        cellvars = self.load()
        filename = self.load()
        name = self.load()
        firstlineno = _r_long(self)
        lnotab = self.load()
        if isinstance(name, bytes):
            name = name.decode()
        return Code2(
            argcount,
            nlocals,
            stacksize,
            flags,
            code,
            consts,
            names,
            varnames,
            filename.decode(),
            name,
            firstlineno,
            lnotab,
            freevars,
            cellvars,
        )

    dispatch[TYPE_CODE] = load_code

    def load_set(self):
        n = _r_long(self)
        args = [self.load() for i in range(n)]
        return set(args)

    dispatch[TYPE_SET] = load_set

    def load_frozenset(self):
        n = _r_long(self)
        args = [self.load() for i in range(n)]
        return frozenset(args)

    dispatch[TYPE_FROZENSET] = load_frozenset


_load_dispatch = _FastUnmarshaller.dispatch

# _________________________________________________________________
#
# user interface

version = 1


@builtinify
def dump(
    x,
    f,
    python_version: tuple = PYTHON_VERSION_TRIPLE,
    is_pypy: Optional[bool] = None,
) -> None:
    # XXX 'version' is ignored, we always dump in a version-0-compatible format
    m = _Marshaller(f.write, python_version, is_pypy)
    m.dump(x)


@builtinify
def load(f, python_version: tuple = PYTHON_VERSION_TRIPLE, is_pypy=None):
    um = _Unmarshaller(f.read, python_version, is_pypy)
    return um.load()


@builtinify
def dumps(
    x,
    python_version: tuple = PYTHON_VERSION_TRIPLE,
    is_pypy: Optional[bool] = None,
):
    buffer = []
    collection_order = x.collection_order if hasattr(x, "collection_order") else {}
    reference_objects = (
        x.reference_objects if hasattr(x, "reference_objects") else set()
    )
    m = _Marshaller(
        buffer.append,
        python_version=python_version,
        is_pypy=is_pypy,
        collection_order=collection_order,
        reference_objects=reference_objects,
    )
    flag_ref = FLAG_REF if python_version >= (3, 4) else 0
    m.dump(x, flag_ref)
    if python_version:
        is_python3 = python_version >= (3, 0)
    else:
        is_python3 = True

    if is_python3:
        if PYTHON_VERSION_TRIPLE >= (3, 0):
            # Python 3.x handling  Python 3.x
            buf = []
            for b in buffer:
                if isinstance(b, str):
                    s2b = bytes(ord(b[j]) for j in range(len(b)))
                    buf.append(s2b)
                elif isinstance(b, bytearray):
                    buf.append(str(b))
                else:
                    buf.append(b)
            return b"".join(buf)
        else:
            # Python 2.x handling Python 3.x
            buf = b""
            for b in buffer:
                buf += b.decode(errors="ignore")
                pass
            return buf
    else:
        # Python 2 or 3 handling Python 2.x
        buf = []
        for b in buffer:
            if isinstance(b, str):
                if python_version < (2, 0):
                    # Python 1.x has no notion of Unicode. It uses strings.
                    buf.append(b)
                else:
                    try:
                        s2b = bytes(ord(b[j]) for j in range(len(b)))
                    except ValueError:
                        s2b = b.encode("utf-8")
                    buf.append(s2b)
            elif isinstance(b, bytearray):
                buf.append(str(b))
            else:
                buf.append(b)

        return b"".join(buf)


@builtinify
def loads(s, python_version=None):
    um = _FastUnmarshaller(s, python_version)
    return um.load()
