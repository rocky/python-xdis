# (C) Copyright 2018-2024 by Rocky Bernstein
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

# NOTE: This module is used in the Python3 interpreter, but also by
# the "sandboxed" process.  It must work for Python2 as well.

import struct
import types

from xdis.codetype import Code2, Code3
from xdis.version_info import PYTHON3, PYTHON_VERSION_TRIPLE, version_tuple_to_str

try:
    intern
except NameError:
    from sys import intern

try:
    from __pypy__ import builtinify

except ImportError:

    def builtinify(f):
        return f


@builtinify
def Ord(c):
    return c if PYTHON3 else ord(c)


TYPE_NULL = "0"
TYPE_NONE = "N"
TYPE_FALSE = "F"
TYPE_TRUE = "T"
TYPE_STOPITER = "S"
TYPE_ELLIPSIS = "."
TYPE_INT = "i"
TYPE_INT64 = "I"  # Python 3.4 removed this
TYPE_FLOAT = "f"  # Seems not in use after Python 2.4
TYPE_BINARY_FLOAT = "g"
TYPE_COMPLEX = "x"
TYPE_BINARY_COMPLEX = "y"  # 3.x
TYPE_LONG = "l"
TYPE_STRING = "s"
TYPE_INTERNED = "t"
TYPE_REF = "r"  # Since 3.4
TYPE_STRINGREF = "R"  # Python 2
TYPE_TUPLE = "("
TYPE_LIST = "["
TYPE_DICT = "{"
TYPE_CODE_OLD = "C"  # used in Python 1.0 - 1.2
TYPE_CODE = "c"
TYPE_UNICODE = "u"
TYPE_UNKNOWN = "?"
TYPE_SET = "<"
TYPE_FROZENSET = ">"

TYPE_ASCII = "a"  # since 3.4
TYPE_ASCII_INTERNED = "A"  # since 3.4
TYPE_SMALL_TUPLE = ")"  # since 3.4
TYPE_SHORT_ASCII = "z"  # since 3.4
TYPE_SHORT_ASCII_INTERNED = "Z"  # since 3.4


class _Marshaller:
    """Python marshalling routine that runs in Python 2 and Python 3.
    We also extend to allow for xdis Code2 and Code3 types and instances.
    """

    dispatch = {}

    def __init__(self, writefunc, python_version=None):
        self._write = writefunc
        self.python_version = python_version

    def dump(self, x):
        if (
            isinstance(x, types.CodeType)
            and PYTHON_VERSION_TRIPLE[:2] != self.python_version[:2]
        ):
            raise RuntimeError(
                "code type passed for version %s but we are running version %s"
                % (version_tuple_to_str(), self.python_version)
            )
        try:
            self.dispatch[type(x)](self, x)
        except KeyError:
            if isinstance(x, Code3):
                self.dispatch[Code3](self, x)
                return
            elif isinstance(x, Code2):
                self.dispatch[Code2](self, x)
                return
            else:
                for tp in type(x).mro():
                    func = self.dispatch.get(tp)
                    if func:
                        break
                else:
                    raise ValueError("unmarshallable object")
            func(self, x)

    def w_long64(self, x):
        self.w_long(x)
        self.w_long(x >> 32)

    def w_long(self, x):
        a = chr(x & 0xFF)
        x >>= 8
        b = chr(x & 0xFF)
        x >>= 8
        c = chr(x & 0xFF)
        x >>= 8
        d = chr(x & 0xFF)
        self._write(a + b + c + d)

    def w_short(self, x):
        self._write(chr(x & 0xFF))
        self._write(chr((x >> 8) & 0xFF))

    def dump_none(self, x):
        self._write(TYPE_NONE)

    dispatch[type(None)] = dump_none

    def dump_bool(self, x):
        if x:
            self._write(TYPE_TRUE)
        else:
            self._write(TYPE_FALSE)

    dispatch[bool] = dump_bool

    def dump_stopiter(self, x):
        if x is not StopIteration:
            raise ValueError("unmarshallable object")
        self._write(TYPE_STOPITER)

    dispatch[type(StopIteration)] = dump_stopiter

    def dump_ellipsis(self, x):
        self._write(TYPE_ELLIPSIS)

    try:
        dispatch[type(Ellipsis)] = dump_ellipsis
    except NameError:
        pass

    # In Python3, this function is not used; see dump_long() below.
    def dump_int(self, x):
        y = x >> 31
        if y and y != -1:
            self._write(TYPE_INT64)
            self.w_long64(x)
        else:
            self._write(TYPE_INT)
            self.w_long(x)

    dispatch[int] = dump_int

    def dump_long(self, x):
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

    def dump_float(self, x):
        write = self._write
        write(TYPE_FLOAT)
        s = repr(x)
        write(chr(len(s)))
        write(s)

    dispatch[float] = dump_float

    def dump_binary_float(self, x):
        write = self._write
        write(TYPE_BINARY_FLOAT)
        write(struct.pack("<d", x))

    dispatch[TYPE_BINARY_FLOAT] = dump_float

    def dump_complex(self, x):
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

    def dump_binary_complex(self, x):
        write = self._write
        write(TYPE_BINARY_COMPLEX)
        write(struct.pack("<d", x.real))
        write(struct.pack("<d", x.imag))

    dispatch[TYPE_BINARY_COMPLEX] = dump_binary_complex

    def dump_string(self, x):
        # XXX we can't check for interned strings, yet,
        # so we (for now) never create TYPE_INTERNED or TYPE_STRINGREF
        self._write(TYPE_STRING)
        self.w_long(len(x))
        self._write(x)

    if PYTHON_VERSION_TRIPLE > (2, 5):
        dispatch[bytes] = dump_string
        dispatch[bytearray] = dump_string

    def dump_unicode(self, x):
        self._write(TYPE_UNICODE)
        if not PYTHON3 and self.python_version < (3, 0):
            s = x.encode("utf8")
        else:
            s = x
        self.w_long(len(s))
        self._write(s)

    try:
        unicode
    except NameError:
        dispatch[str] = dump_unicode
    else:
        dispatch[unicode] = dump_unicode  # noqa

    def dump_tuple(self, x):
        self._write(TYPE_TUPLE)
        self.w_long(len(x))
        for item in x:
            self.dump(item)

    dispatch[tuple] = dump_tuple
    dispatch[TYPE_TUPLE] = dump_tuple

    def dump_small_tuple(self, x):
        self._write(TYPE_SMALL_TUPLE)
        self.w_short(len(x))
        for item in x:
            self.dump(item)

    dispatch[TYPE_SMALL_TUPLE] = dump_small_tuple

    def dump_list(self, x):
        self._write(TYPE_LIST)
        self.w_long(len(x))
        for item in x:
            self.dump(item)

    dispatch[list] = dump_list
    dispatch[TYPE_LIST] = dump_tuple

    def dump_dict(self, x):
        self._write(TYPE_DICT)
        for key, value in x.items():
            self.dump(key)
            self.dump(value)
        self._write(TYPE_NULL)

    dispatch[dict] = dump_dict

    def dump_code2(self, x):
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
    def dump_code3(self, x):
        self._write(TYPE_CODE)
        self.w_long(x.co_argcount)
        if hasattr(x, "co_posonlyargcount"):
            self.w_long(x.co_posonlyargcount)
        self.w_long(x.co_kwonlyargcount)
        self.w_long(x.co_nlocals)
        self.w_long(x.co_stacksize)
        self.w_long(x.co_flags)
        self.dump(x.co_code)
        self.dump(x.co_consts)
        self.dump(x.co_names)
        self.dump(x.co_varnames)
        self.dump(x.co_freevars)
        self.dump(x.co_cellvars)
        self.dump(x.co_filename)
        self.dump(x.co_name)
        self.w_long(x.co_firstlineno)
        # 3.10 and greater uses co_linetable.
        linetable = x.co_linetable if hasattr(x, "co_linetable") else x.co_lnotab

        self.dump(linetable)

    dispatch[Code3] = dump_code3

    try:
        if PYTHON3:
            dispatch[types.CodeType] = dump_code3
        else:
            dispatch[types.CodeType] = dump_code2
    except NameError:
        pass

    def dump_set(self, x):
        self._write(TYPE_SET)
        self.w_long(len(x))
        for each in x:
            self.dump(each)

    try:
        dispatch[set] = dump_set
    except NameError:
        pass

    def dump_frozenset(self, x):
        self._write(TYPE_FROZENSET)
        self.w_long(len(x))
        for each in x:
            self.dump(each)

    try:
        dispatch[frozenset] = dump_frozenset
    except NameError:
        pass

    # FIXME: dump_ascii, dump_short_ascii are just guesses
    def dump_ascii(self, x):
        self._write(TYPE_ASCII)
        self.w_long(len(x))
        self._write(x)

    dispatch[TYPE_ASCII] = dump_ascii

    def dump_short_ascii(self, x):
        self._write(TYPE_SHORT_ASCII)
        # FIXME: check len(x)?
        self.w_short(len(x))
        self._write(x)

    dispatch[TYPE_SHORT_ASCII] = dump_short_ascii

    # FIXME: Handle interned versions of dump_ascii, dump_short_ascii


class _NULL:
    pass


class _StringBuffer:
    def __init__(self, value):
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

    def __init__(self, readfunc, python_version=None):
        self._read = readfunc
        self._stringtable = []
        self.python_version = python_version

    def load(self):
        c = self._read(1)
        if not c:
            raise EOFError
        try:
            return self.dispatch[c](self)
        except KeyError:
            raise ValueError("bad marshal code: %c (%d)" % (c, Ord(c)))

    def r_byte(self):
        return Ord(self._read(1))

    def r_short(self):
        lo = Ord(self._read(1))
        hi = Ord(self._read(1))
        x = lo | (hi << 8)
        if x & 0x8000:
            x = x - 0x10000
        return x

    def r_long(self):
        s = self._read(4)
        a = Ord(s[0])
        b = Ord(s[1])
        c = Ord(s[2])
        d = Ord(s[3])
        x = a | (b << 8) | (c << 16) | (d << 24)
        if d & 0x80 and x > 0:
            x = -((1 << 32) - x)
            return int(x)
        else:
            return x

    def r_long64(self):
        a = Ord(self._read(1))
        b = Ord(self._read(1))
        c = Ord(self._read(1))
        d = Ord(self._read(1))
        e = Ord(self._read(1))
        f = Ord(self._read(1))
        g = Ord(self._read(1))
        h = Ord(self._read(1))
        x = a | (b << 8) | (c << 16) | (d << 24)
        x = x | (e << 32) | (f << 40) | (g << 48) | (h << 56)
        if h & 0x80 and x > 0:
            x = -((1 << 64) - x)
        return x

    def load_null(self):
        return _NULL

    dispatch[TYPE_NULL] = load_null

    def load_none(self):
        return None

    dispatch[TYPE_NONE] = load_none

    def load_true(self):
        return True

    dispatch[TYPE_TRUE] = load_true

    def load_false(self):
        return False

    dispatch[TYPE_FALSE] = load_false

    def load_ascii(self):
        return self.r_byte()

    dispatch[TYPE_ASCII] = load_null

    def load_stopiter(self):
        return StopIteration

    dispatch[TYPE_STOPITER] = load_stopiter

    def load_ellipsis(self):
        return Ellipsis

    dispatch[TYPE_ELLIPSIS] = load_ellipsis

    dispatch[TYPE_INT] = r_long

    dispatch[TYPE_INT64] = r_long64

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

    def load_float(self):
        n = Ord(self._read(1))
        s = self._read(n)
        return float(s)

    dispatch[TYPE_FLOAT] = load_float

    def load_binary_float(self):
        f = self._read(8)
        return float(struct.unpack("<d", f)[0])

    dispatch[TYPE_BINARY_FLOAT] = load_binary_float

    def load_complex(self):
        n = Ord(self._read(1))
        s = self._read(n)
        real = float(s)
        n = Ord(self._read(1))
        s = self._read(n)
        imag = float(s)
        return complex(real, imag)

    dispatch[TYPE_COMPLEX] = load_complex

    def load_string(self):
        n = self.r_long()
        return self._read(n)

    dispatch[TYPE_STRING] = load_string

    def load_interned(self):
        n = self.r_long()
        ret = intern(self._read(n))
        self._stringtable.append(ret)
        return ret

    dispatch[TYPE_INTERNED] = load_interned

    def load_stringref(self):
        n = self.r_long()
        return self._stringtable[n]

    dispatch[TYPE_STRINGREF] = load_stringref

    def load_unicode(self):
        n = self.r_long()
        s = self._read(n)
        ret = s.decode("utf8")
        return ret

    dispatch[TYPE_UNICODE] = load_unicode

    def load_tuple(self):
        return tuple(self.load_list())

    dispatch[TYPE_TUPLE] = load_tuple

    def load_list(self):
        n = self.r_long()
        list = [self.load() for i in range(n)]
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
        argcount = self.r_long()
        if self.python_version and self.python_version >= "3.0":
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
            if PYTHON3:
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
                return Code3(
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
            if PYTHON3:
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
            else:
                return types.CodeType(
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

    def load_set(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return set(args)

    dispatch[TYPE_SET] = load_set

    def load_frozenset(self):
        n = self.r_long()
        args = [self.load() for i in range(n)]
        return frozenset(args)

    dispatch[TYPE_FROZENSET] = load_frozenset


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
    lo = Ord(_read1(self))
    hi = Ord(_read1(self))
    x = lo | (hi << 8)
    if x & 0x8000:
        x = x - 0x10000
    return x


def _r_long(self):
    # inlined this most common case
    p = self.bufpos
    s = self.bufstr
    a = Ord(s[p])
    b = Ord(s[p + 1])
    c = Ord(s[p + 2])
    d = Ord(s[p + 3])
    self.bufpos += 4
    x = a | (b << 8) | (c << 16) | (d << 24)
    if d & 0x80 and x > 0:
        x = -((1 << 32) - x)
        return int(x)
    else:
        return x


def _r_long64(self):
    a = Ord(_read1(self))
    b = Ord(_read1(self))
    c = Ord(_read1(self))
    d = Ord(_read1(self))
    e = Ord(_read1(self))
    f = Ord(_read1(self))
    g = Ord(_read1(self))
    h = Ord(_read1(self))
    x = a | (b << 8) | (c << 16) | (d << 24)
    x = x | (e << 32) | (f << 40) | (g << 48) | (h << 56)
    if h & 0x80 and x > 0:
        x = -((1 << 64) - x)
    return x


_load_dispatch = {}


class _FastUnmarshaller:
    dispatch = {}

    def __init__(self, buffer, python_version=None):
        self.bufstr = buffer
        self.bufpos = 0
        self._stringtable = []
        self.python_version = python_version

    def load(self):
        # make flow space happy
        c = "?"
        try:
            c = self.bufstr[self.bufpos]
            if PYTHON3:
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

    def load_none(self):
        return None

    dispatch[TYPE_NONE] = load_none

    def load_true(self):
        return True

    dispatch[TYPE_TRUE] = load_true

    def load_false(self):
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

    def load_float(self):
        n = Ord(_read1(self))
        s = _read(self, n)
        return float(s)

    dispatch[TYPE_FLOAT] = load_float

    def load_complex(self):
        n = Ord(_read1(self))
        s = _read(self, n)
        real = float(s)
        n = Ord(_read1(self))
        s = _read(self, n)
        imag = float(s)
        return complex(real, imag)

    dispatch[TYPE_COMPLEX] = load_complex

    def load_string(self):
        n = _r_long(self)
        return _read(self, n)

    dispatch[TYPE_STRING] = load_string

    def load_interned(self):
        n = _r_long(self)
        s = _read(self, n)
        if PYTHON3:
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
        if PYTHON3:
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
        else:
            return types.CodeType(
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
def dump(x, f, version=version, python_version=None):
    # XXX 'version' is ignored, we always dump in a version-0-compatible format
    m = _Marshaller(f.write, python_version)
    m.dump(x)


@builtinify
def load(f, python_version=None):
    um = _Unmarshaller(f.read, python_version)
    return um.load()


@builtinify
def dumps(x, version=version, python_version=PYTHON_VERSION_TRIPLE):
    # XXX 'version' is ignored, we always dump in a version-0-compatible format
    buffer = []
    m = _Marshaller(buffer.append, python_version=python_version)
    m.dump(x)
    if python_version:
        is_python3 = python_version >= (3, 0)
    else:
        is_python3 = PYTHON3

    if is_python3:
        if PYTHON_VERSION_TRIPLE >= (3, 0):
            # Python 3.x handling  Python 3.x
            buf = []
            for b in buffer:
                if isinstance(b, str) and PYTHON3:
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
            if isinstance(b, str) and PYTHON3:
                try:
                    s2b = bytes(ord(b[j]) for j in range(len(b)))
                except ValueError:
                    s2b = b.encode("utf-8")
                buf.append(s2b)
            elif isinstance(b, bytearray):
                buf.append(str(b))
            else:
                buf.append(b)

        return "".join(buf)


@builtinify
def loads(s, python_version=None):
    um = _FastUnmarshaller(s, python_version)
    return um.load()
