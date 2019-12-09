# Copyright (c) 2015-2019 by Rocky Bernstein
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

"""
CPython magic- and version-independent Python object
deserialization (unmarshal).

This is needed when the bytecode extracted is from
a different version than the currently-running Python.

When the two are the same, you can simply use Python's built-in marshal.loads()
to produce a code object
"""

import sys, types
from struct import unpack

from xdis.magics import PYTHON_MAGIC_INT, IS_PYPY3
from xdis.code import Code2, Code3, Code38, Code2Compat
from xdis import PYTHON3, PYTHON_VERSION, IS_PYPY

internStrings = []
internObjects = []

if PYTHON3:

    def long(n):
        return n


else:
    import unicodedata


def compat_str(s):
    if PYTHON3:
        try:
            return s.decode("utf-8")
        except UnicodeDecodeError:
            # If not Unicode, return bytes
            # and it will get converted to str when needed
            return s

        return s.decode()
    else:
        return str(s)


def compat_u2s(u):
    if PYTHON_VERSION < 3.0:
        # See also unaccent.py which can be found using google. I
        # found it and this code via
        # https://www.peterbe.com/plog/unicode-to-ascii where it is a
        # dead link. That can potentially do better job in converting accents.
        s = unicodedata.normalize("NFKD", u)
        try:
            return s.encode("ascii")
        except UnicodeEncodeError:
            return s
    else:
        return str(u)


def load_code(fp, magic_int, code_objects={}):
    """
    marshal.load() written in Python. When the Python bytecode magic loaded is the
    same magic for the running Python interpreter, we can simply use the
    Python-supplied marshal.load().

    However we need to use this when versions are different since the internal
    code structures are different. Sigh.
    """
    global internStrings, internObjects
    internStrings = []
    internObjects = []
    seek_pos = fp.tell()
    # Do a sanity check. Is this a code type?
    b = ord(fp.read(1))

    save_ref = False
    if b & 0x80:
        save_ref = True
        internObjects.append(None)
        b = b & 0x7F

    c = chr(b)
    if c == "c" or (magic_int in (39170, 39171) and c == "C"):
        fp.seek(seek_pos)
    else:
        raise TypeError(
            "File %s doesn't smell like Python bytecode:\n"
            "expecting code indicator 'c'; got '%s'" % (fp.name, c)
        )

    code = load_code_internal(fp, magic_int, code_objects=code_objects)
    if save_ref:
        internObjects[0] = code
    return code


def load_code_type(fp, magic_int, bytes_for_s=False, code_objects={}):
    # FIXME: use tables to simplify this?
    # Python [1.0 .. 2.2)

    v10_to_12 = magic_int in (39170, 39171)

    # FIXME: find out what magics were for 1.3
    v13_to_22 = magic_int in (11913, 5892, 20121, 50428, 50823, 60202, 60717)
    v11_to_14 = magic_int in (39170, 39171, 11913, 5892)

    # Python [1.5 .. 2.2)
    v15_to_22 = magic_int in (20121, 50428, 50823, 60202, 60717)
    v13_to_20 = magic_int in (11913, 5892, 20121, 50428, 50823)
    v21_to_27 = not v13_to_20 and 60202 <= magic_int <= 63000

    if v13_to_22:
        co_argcount = unpack("<h", fp.read(2))[0]
    elif v10_to_12:
        co_argcount = 0
    else:
        co_argcount = unpack("<i", fp.read(4))[0]

    if magic_int in (3412, 3413, 3422):
        co_posonlyargcount = unpack("<i", fp.read(4))[0]
    else:
        co_posonlyargcount = None

    if ((3020 < magic_int < 20121) or magic_int in (64, 160, 112, 192)) and not v11_to_14:
        kwonlyargcount = unpack("<i", fp.read(4))[0]
    else:
        kwonlyargcount = 0

    if v13_to_22:
        co_nlocals = unpack("<h", fp.read(2))[0]
    elif v10_to_12:
        co_nlocals = 0
    else:
        co_nlocals = unpack("<i", fp.read(4))[0]

    if v15_to_22:
        co_stacksize = unpack("<h", fp.read(2))[0]
    elif v11_to_14 or v10_to_12:
        co_stacksize = 0
    else:
        co_stacksize = unpack("<i", fp.read(4))[0]

    if v13_to_22:
        co_flags = unpack("<h", fp.read(2))[0]
    elif v10_to_12:
        co_flags = 0
    else:
        co_flags = unpack("<i", fp.read(4))[0]

    co_code = load_code_internal(
        fp, magic_int, bytes_for_s=True, code_objects=code_objects
    )
    co_consts = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_names = load_code_internal(fp, magic_int, code_objects=code_objects)

    # FIXME: only if >= 1.3
    if v10_to_12:
        co_varnames = []
    else:
        co_varnames = load_code_internal(fp, magic_int, code_objects=code_objects)

    if not (v13_to_20 or v10_to_12):
        co_freevars = load_code_internal(fp, magic_int, code_objects=code_objects)
        co_cellvars = load_code_internal(fp, magic_int, code_objects=code_objects)
    else:
        co_freevars = tuple()
        co_cellvars = tuple()

    co_filename = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_name = load_code_internal(fp, magic_int)

    if v15_to_22:
        co_firstlineno = unpack("<h", fp.read(2))[0]
    elif v11_to_14:
        # < 1.5 there is no lnotab, so no firstlineno.
        # SET_LINENO is used instead.
        co_firstlineno = -1  # Bogus sentinal value
    else:
        co_firstlineno = unpack("<i", fp.read(4))[0]

    if v11_to_14:
        # < 1.5 uses SET_LINENO only
        co_lnotab = ""
    else:
        co_lnotab = load_code_internal(fp, magic_int, code_objects=code_objects)

    # The Python3 code object is different than Python2's which
    # we are reading if we get here.
    # Also various parameters which were strings are now
    # bytes (which is probably more logical).
    if PYTHON3:
        Code = types.CodeType
        if PYTHON_MAGIC_INT > 3020 or PYTHON_MAGIC_INT in IS_PYPY3:
            # Check for Python 3 interpreter reading Python 2 bytecode.
            # Python 3's code objects are bytes while Python 2's are strings.
            #
            # In later Python3 magic_ints, there is a
            # kwonlyargcount parameter which we set to 0.
            if v10_to_12 or v13_to_22 or v21_to_27:
                code = Code2(
                    co_argcount,
                    kwonlyargcount,
                    co_nlocals,
                    co_stacksize,
                    co_flags,
                    co_code,
                    co_consts,
                    co_names,
                    co_varnames,
                    co_filename,
                    co_name,
                    co_firstlineno,
                    co_lnotab,
                    co_freevars,
                    co_cellvars,
                )
            else:
                if PYTHON_MAGIC_INT in (3412, 3413, 3422):
                    if co_posonlyargcount is not None:
                        # Python3.8 to Python3.9: Ok to use native Python3.8's code type
                        code = Code(
                            co_argcount,
                            co_posonlyargcount,
                            kwonlyargcount,
                            co_nlocals,
                            co_stacksize,
                            co_flags,
                            co_code,
                            co_consts,
                            co_names,
                            co_varnames,
                            co_filename,
                            co_name,
                            co_firstlineno,
                            bytes(co_lnotab, encoding="utf-8"),
                            co_freevars,
                            co_cellvars,
                        )
                    else:
                        if not isinstance(co_lnotab, bytes):
                            co_lnotab = bytes(co_lnotab, encoding="utf-8")
                        code = Code3(
                            co_argcount,
                            kwonlyargcount,
                            co_nlocals,
                            co_stacksize,
                            co_flags,
                            co_code,
                            co_consts,
                            co_names,
                            co_varnames,
                            co_filename,
                            co_name,
                            co_firstlineno,
                            co_lnotab,
                            co_freevars,
                            co_cellvars,
                        )
                elif co_posonlyargcount is not None:
                    if not isinstance(co_lnotab, bytes):
                        co_lnotab = bytes(co_lnotab, encoding="utf-8")
                    code = Code38(
                        co_argcount,
                        co_posonlyargcount,
                        kwonlyargcount,
                        co_nlocals,
                        co_stacksize,
                        co_flags,
                        co_code,
                        co_consts,
                        co_names,
                        co_varnames,
                        co_filename,
                        co_name,
                        co_firstlineno,
                        co_lnotab,
                        co_freevars,
                        co_cellvars,
                    )

                else:
                    # Python3 (< 3.8) to Python3: Ok to use native Python3's code type
                    if not isinstance(co_lnotab, bytes):
                        co_lnotab = bytes(co_lnotab, encoding="utf-8")
                    code = Code(
                        co_argcount,
                        kwonlyargcount,
                        co_nlocals,
                        co_stacksize,
                        co_flags,
                        co_code,
                        co_consts,
                        co_names,
                        co_varnames,
                        co_filename,
                        co_name,
                        co_firstlineno,
                        co_lnotab,
                        co_freevars,
                        co_cellvars,
                    )
                    pass
                pass
        else:
            code = Code(
                co_argcount,
                kwonlyargcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                tuple(co_consts),
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_firstlineno,
                bytes(co_lnotab, encoding="utf-8"),
                co_freevars,
                co_cellvars,
            )
    else:
        if v11_to_14:
            code = Code2Compat(
                co_argcount,
                co_nlocals,
                co_stacksize,
                co_flags,
                co_code,
                co_consts,
                co_names,
                co_varnames,
                co_filename,
                co_name,
                co_firstlineno,
                co_lnotab,
                co_freevars,
                co_cellvars,
            )
        else:
            if 3000 <= magic_int < 20121:
                # Python 3 encodes some fields as Unicode while Python2
                # requires the corresponding field to have string values
                co_consts = tuple(
                    [compat_u2s(s) if isinstance(s, unicode) else s for s in co_consts]
                )
                co_names = tuple(
                    [compat_u2s(s) if isinstance(s, unicode) else s for s in co_names]
                )
                co_varnames = tuple(
                    [
                        compat_u2s(s) if isinstance(s, unicode) else s
                        for s in co_varnames
                    ]
                )
                co_filename = str(co_filename)
                co_name = str(co_name)

            if 3020 < magic_int <= 20121 or magic_int in IS_PYPY3:
                code = Code3(
                    co_argcount,
                    kwonlyargcount,
                    co_nlocals,
                    co_stacksize,
                    co_flags,
                    co_code,
                    co_consts,
                    co_names,
                    co_varnames,
                    co_filename,
                    co_name,
                    co_firstlineno,
                    co_lnotab,
                    co_freevars,
                    co_cellvars,
                )
            else:
                if magic_int in (160, 192):
                    co_filename = str(co_filename)
                    co_name = str(co_name)
                    co_varnames = tuple([str(t) for t in co_varnames])
                    co_consts = tuple([str(t) for t in co_consts])
                    co_freevars = tuple([str(t) for t in co_freevars])
                    co_cellvars = tuple([str(t) for t in co_cellvars])

                Code = types.CodeType
                code = Code(
                    co_argcount,
                    co_nlocals,
                    co_stacksize,
                    co_flags,
                    co_code,
                    co_consts,
                    co_names,
                    co_varnames,
                    co_filename,
                    co_name,
                    co_firstlineno,
                    co_lnotab,
                    co_freevars,
                    co_cellvars,
                )
                pass
            pass
        pass
    code_objects[str(code)] = code
    return code


# Python 3.4+ support for reference objects.
# The names follow marshal.c
def r_ref_reserve(obj, flag):
    i = None
    if flag:
        i = len(internObjects)
        internObjects.append(obj)
    return obj, i


def r_ref_insert(obj, i):
    if i is not None:
        internObjects[i] = obj
    return obj


def r_ref(obj, flag):
    if flag:
        internObjects.append(obj)
    return obj


# Bit set on marshalType if we should
# add obj to internObjects.
# FLAG_REF is the marchal.c name
FLAG_REF = 0x80

# The keys in following dictionary are an unmashal codes, like "s", "c", "<", etc.
# the values of the dictionary are routines to call that do the data unmarshaling.
#
# Note: we could eliminate the parameters, if this were all inside a
# class.  This might be good from an efficiency standpoint, and bad
# from a functional-programming standpoint. Pick your poison.
UNMARSHAL_DISPATCH_TABLE = {}


# In C this NULL. Not sure what it should
# translate here. Note NULL != None which is below
def t_C_NULL(fp, flag=None, bytes_for_s=None, magic_int=None, code_objects=None):
    return None


UNMARSHAL_DISPATCH_TABLE["0"] = t_C_NULL


def t_None(fp=None, flag=None, bytes_for_s=None, magic_int=None, code_objects=None):
    return None


UNMARSHAL_DISPATCH_TABLE["N"] = t_None


def t_stopIteration(
    fp=None, flag=None, bytes_for_s=None, magic_int=None, code_objects=None
):
    return StopIteration


UNMARSHAL_DISPATCH_TABLE["S"] = t_stopIteration


def t_Elipsis(fp=None, flag=None, bytes_for_s=None, magic_int=None, code_objects=None):
    return Ellipsis


UNMARSHAL_DISPATCH_TABLE["."] = t_Elipsis


def t_False(fp=None, flag=None, bytes_for_s=None, magic_int=None, code_objects=None):
    return False


UNMARSHAL_DISPATCH_TABLE["F"] = t_False


def t_True(fp=None, flag=None, bytes_for_s=None, magic_int=None, code_objects=None):
    return True


UNMARSHAL_DISPATCH_TABLE["T"] = t_True


def t_int32(fp, flag, bytes_for_s=None, magic_int=None, code_objects=None):
    return r_ref(int(unpack("<i", fp.read(4))[0]), flag)


UNMARSHAL_DISPATCH_TABLE["i"] = t_int32


def t_long(fp, flag, bytes_for_s=None, magic_int=None, code_objects=None):
    n = unpack("<i", fp.read(4))[0]
    if n == 0:
        return long(0)
    size = abs(n)
    d = long(0)
    for j in range(0, size):
        md = int(unpack("<h", fp.read(2))[0])
        d += md << j * 15
    if n < 0:
        d = long(d * -1)
    return r_ref(d, flag)


UNMARSHAL_DISPATCH_TABLE["l"] = t_long

# Python 3.4 removed this.
def t_int64(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    obj = unpack("<q", fp.read(8))[0]
    if save_ref:
        internObjects.append(obj)
    return obj


UNMARSHAL_DISPATCH_TABLE["I"] = t_int64

# float - Seems not in use after Python 2.4
def t_float(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    strsize = unpack("B", fp.read(1))[0]
    s = fp.read(strsize)
    return r_ref(float(s), save_ref)


UNMARSHAL_DISPATCH_TABLE["f"] = t_float


def t_binary_float(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    return r_ref(float(unpack("<d", fp.read(8))[0]), save_ref)


UNMARSHAL_DISPATCH_TABLE["g"] = t_binary_float


def t_complex(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    if magic_int <= 62061:
        get_float = lambda: float(fp.read(unpack("B", fp.read(1))[0]))
    else:
        get_float = lambda: float(fp.read(unpack("<i", fp.read(4))[0]))
    real = get_float()
    imag = get_float()
    return r_ref(complex(real, imag), save_ref)


UNMARSHAL_DISPATCH_TABLE["x"] = t_complex


def t_binary_complex(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    # binary complex
    real = unpack("<d", fp.read(8))[0]
    imag = unpack("<d", fp.read(8))[0]
    return r_ref(complex(real, imag), save_ref)


UNMARSHAL_DISPATCH_TABLE["y"] = t_binary_complex

# Note: could mean bytes in Python3 processing Python2 bytecode
def t_string(fp, save_ref, bytes_for_s, magic_int=None, code_objects=None):
    strsize = unpack("<i", fp.read(4))[0]
    s = fp.read(strsize)
    if not bytes_for_s:
        s = compat_str(s)
    return r_ref(s, save_ref)


UNMARSHAL_DISPATCH_TABLE["s"] = t_string

# Python 3.4
def t_ASCII_interned(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    # FIXME: check
    strsize = unpack("<i", fp.read(4))[0]
    interned = compat_str(fp.read(strsize))
    internStrings.append(interned)
    return r_ref(interned, save_ref)


UNMARSHAL_DISPATCH_TABLE["A"] = t_ASCII_interned

# Since Python 3.4
def t_ASCII(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    strsize = unpack("<i", fp.read(4))[0]
    s = fp.read(strsize)
    s = compat_str(s)
    return r_ref(s, save_ref)


UNMARSHAL_DISPATCH_TABLE["a"] = t_ASCII

# Since Python 3.4
def t_short_ASCII(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    strsize = unpack("B", fp.read(1))[0]
    return r_ref(compat_str(fp.read(strsize)), save_ref)


UNMARSHAL_DISPATCH_TABLE["z"] = t_short_ASCII

# Since Python 3.4
def t_short_ASCII_interned(
    fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None
):
    # FIXME: check
    strsize = unpack("B", fp.read(1))[0]
    interned = compat_str(fp.read(strsize))
    internStrings.append(interned)
    return r_ref(interned, save_ref)


UNMARSHAL_DISPATCH_TABLE["Z"] = t_short_ASCII_interned


# Since Python 3.4
def t_interned(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    strsize = unpack("<i", fp.read(4))[0]
    interned = compat_str(fp.read(strsize))
    internStrings.append(interned)
    return r_ref(interned, save_ref)


UNMARSHAL_DISPATCH_TABLE["t"] = t_interned


def t_unicode(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    strsize = unpack("<i", fp.read(4))[0]
    unicodestring = fp.read(strsize)
    if PYTHON_VERSION == 3.2 and IS_PYPY:
        # FIXME: this isn't quite right. See
        # pypy3-2.4.0/lib-python/3/email/message.py
        # '([^\ud800-\udbff]|\A)[\udc00-\udfff]([^\udc00-\udfff]|\Z)')
        return r_ref(unicodestring.decode("utf-8", errors="ignore"), save_ref)
    else:
        return r_ref(unicodestring.decode("utf-8"), save_ref)


UNMARSHAL_DISPATCH_TABLE["u"] = t_unicode


# Since Python 3.4
def t_small_tuple(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    # small tuple - since Python 3.4
    tuplesize = unpack("B", fp.read(1))[0]
    ret, i = r_ref_reserve(tuple(), save_ref)
    while tuplesize > 0:
        ret += (load_code_internal(fp, magic_int, code_objects=code_objects),)
        tuplesize -= 1
        pass
    return r_ref_insert(ret, i)


UNMARSHAL_DISPATCH_TABLE[")"] = t_small_tuple


def t_tuple(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    tuplesize = unpack("<i", fp.read(4))[0]
    ret = r_ref(tuple(), save_ref)
    while tuplesize > 0:
        ret += (load_code_internal(fp, magic_int, code_objects=code_objects),)
        tuplesize -= 1
    return ret


UNMARSHAL_DISPATCH_TABLE["("] = t_tuple


def t_list(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    # FIXME: check me
    n = unpack("<i", fp.read(4))[0]
    ret = r_ref(list(), save_ref)
    while n > 0:
        ret += (load_code_internal(fp, magic_int, code_objects=code_objects),)
        n -= 1
    return ret


UNMARSHAL_DISPATCH_TABLE["["] = t_list


def t_frozenset(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    setsize = unpack("<i", fp.read(4))[0]
    ret, i = r_ref_reserve(tuple(), save_ref)
    while setsize > 0:
        ret += (load_code_internal(fp, magic_int, code_objects=code_objects),)
        setsize -= 1
    return r_ref_insert(frozenset(ret), i)


UNMARSHAL_DISPATCH_TABLE["<"] = t_frozenset


def t_set(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    setsize = unpack("<i", fp.read(4))[0]
    ret, i = r_ref_reserve(tuple(), save_ref)
    while setsize > 0:
        ret += (load_code_internal(fp, magic_int, code_objects=code_objects),)
        setsize -= 1
    return r_ref_insert(set(ret), i)


UNMARSHAL_DISPATCH_TABLE[">"] = t_set


def t_int32(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    return r_ref(int(unpack("<i", fp.read(4))[0]), save_ref)


UNMARSHAL_DISPATCH_TABLE["i"] = t_int32


def t_dict(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    ret = r_ref(dict(), save_ref)
    # dictionary
    # while True:
    #     key = load_code_internal(fp, magic_int, code_objects=code_objects)
    #     if key is NULL:
    #         break
    #     val = load_code_internal(fp, magic_int, code_objects=code_objects)
    #     if val is NULL:
    #         break
    #     ret[key] = val
    #     pass
    raise KeyError(marshalType)


UNMARSHAL_DISPATCH_TABLE["{"] = t_dict


def t_python2_string_reference(
    fp, save_ref=None, bytes_for_s=None, magic_int=None, code_objects=None
):
    refnum = unpack("<i", fp.read(4))[0]
    return internStrings[refnum]


UNMARSHAL_DISPATCH_TABLE["R"] = t_python2_string_reference


def t_code(fp, save_ref, bytes_for_s=None, magic_int=None, code_objects=None):
    code = load_code_type(fp, magic_int, bytes_for_s=False, code_objects=code_objects)
    if save_ref:
        internObjects.append(code)
    return code


UNMARSHAL_DISPATCH_TABLE["c"] = t_code
UNMARSHAL_DISPATCH_TABLE["C"] = t_code  # Older Python code


# Since Python 3.4
def t_object_reference(
    fp, save_ref=None, bytes_for_s=None, magic_int=None, code_objects=None
):
    refnum = unpack("<i", fp.read(4))[0]
    o = internObjects[refnum]
    return o


UNMARSHAL_DISPATCH_TABLE["r"] = t_object_reference


def t_unknown(fp, save_ref=None, bytes_for_s=None, magic_int=None, code_objects=None):
    raise KeyError(marshalType)


UNMARSHAL_DISPATCH_TABLE["?"] = t_unknown


# In marshal.c this method is called r_object() and is one big case
# statement
def load_code_internal(fp, magic_int, bytes_for_s=False, code_objects={}):
    global internStrings, internObjects

    b1 = ord(fp.read(1))
    save_ref = False
    if b1 & FLAG_REF:
        # Since 3.4, "flag" is the marshal.c name
        save_ref = True
        b1 = b1 & (FLAG_REF - 1)
    marshalType = chr(b1)

    # print(marshalType) # debug
    if marshalType in UNMARSHAL_DISPATCH_TABLE:
        return UNMARSHAL_DISPATCH_TABLE[marshalType](
            fp, save_ref, bytes_for_s, magic_int, code_objects
        )
    else:
        try:
            sys.stderr.write(
                "Unknown type %i (hex %x) %c\n"
                % (ord(marshalType), hex(ord(marshalType)), marshalType)
            )
        except TypeError:
            sys.stderr.write("Unknown type %i %c\n" % (ord(marshalType), marshalType))

    return
