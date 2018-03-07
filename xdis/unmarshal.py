# Copyright (c) 2015-2017 by Rocky Bernstein
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

from xdis.magics import PYTHON_MAGIC_INT
from xdis.code import Code2, Code3
from xdis import PYTHON3, PYTHON_VERSION, IS_PYPY

internStrings = []
internObjects = []

if PYTHON3:
    def long(n): return n
else:
    import unicodedata

def compat_str(s):
    if (PYTHON_VERSION > 3.2 or
        # FIXME: investigate
        PYTHON_VERSION == 3.2 and IS_PYPY):
        return s.decode('utf-8', errors='ignore')
    elif PYTHON3:
        return s.decode()
    else:
        return str(s)

def compat_u2s(u):
    if PYTHON_VERSION < 3.0:
        # See also unaccent.py which can be found using google. I
        # found it and this code via
        # https://www.peterbe.com/plog/unicode-to-ascii where it is a
        # dead link. That can potentially do better job in converting accents.
        return unicodedata.normalize('NFKD', u).encode('ascii', 'ignore')
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
    b =  ord(fp.read(1))

    if (b & 0x80):
        b = b & 0x7f

    c = chr(b)
    if c != 'c':
        raise TypeError("File %s doesn't smell like Python bytecode:\n"
                        "expecting code indicator 'c'; got '%s'"
                        % (fp.name, c))

    fp.seek(seek_pos)
    return load_code_internal(fp, magic_int, code_objects=code_objects)

def load_code_type(fp, magic_int, bytes_for_s=False, code_objects={}):
    # Python [1.3 .. 2.2)
    # FIXME: find out what magics were for 1.3
    v13_to_22 = magic_int in (11913, 5892, 20121, 50428, 50823, 60202, 60717)

    # Python [1.5 .. 2.2)
    v15_to_22 = magic_int in (20121, 50428, 50823, 60202, 60717)
    v15_to_20 = magic_int in (20121, 50428, 50823)
    v13_to_20 = magic_int in (11913, 5892, 20121, 50428, 50823)
    v21_to_27 = not v13_to_20 and 60202 <= magic_int <= 63000

    if v13_to_22:
        co_argcount = unpack('<h', fp.read(2))[0]
    else:
        co_argcount = unpack('<i', fp.read(4))[0]

    if 3020 < magic_int < 20121:
        kwonlyargcount = unpack('<i', fp.read(4))[0]
    else:
        kwonlyargcount = 0

    if v13_to_22:
        co_nlocals = unpack('<h', fp.read(2))[0]
    else:
        co_nlocals = unpack('<i', fp.read(4))[0]

    if v15_to_22:
        co_stacksize = unpack('<h', fp.read(2))[0]
    else:
        co_stacksize = unpack('<i', fp.read(4))[0]

    if v13_to_22:
        co_flags = unpack('<h', fp.read(2))[0]
    else:
        co_flags = unpack('<i', fp.read(4))[0]

    co_code = load_code_internal(fp, magic_int, bytes_for_s=True,
                                 code_objects=code_objects)
    co_consts = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_names = load_code_internal(fp, magic_int, code_objects=code_objects)

    # FIXME: only if >= 1.3
    co_varnames = load_code_internal(fp, magic_int, code_objects=code_objects)

    if not v13_to_20:
        co_freevars = load_code_internal(fp, magic_int, code_objects=code_objects)
        co_cellvars = load_code_internal(fp, magic_int, code_objects=code_objects)
    else:
        co_freevars = tuple()
        co_cellvars = tuple()

    co_filename = load_code_internal(fp, magic_int, code_objects=code_objects)
    co_name = load_code_internal(fp, magic_int)

    if v15_to_22:
        co_firstlineno = unpack('<h', fp.read(2))[0]
    else:
        co_firstlineno = unpack('<i', fp.read(4))[0]

    # FIXME: only if >= 1.5
    co_lnotab = load_code_internal(fp, magic_int, code_objects=code_objects)

    # The Python3 code object is different than Python2's which
    # we are reading if we get here.
    # Also various parameters which were strings are now
    # bytes (which is probably more logical).
    if PYTHON3:
        Code = types.CodeType
        if PYTHON_MAGIC_INT > 3020:
            # Check for Python 3 interpreter reading Python 2 bytecode.
            # Python 3's code objects are bytes while Python 2's are strings.
            #
            # In later Python3 magic_ints, there is a
            # kwonlyargcount parameter which we set to 0.
            if v15_to_20 or v21_to_27:
                code = Code2(co_argcount, kwonlyargcount, co_nlocals, co_stacksize, co_flags,
                             co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                             co_firstlineno, co_lnotab, co_freevars, co_cellvars)
            else:
                # Python3 to Python3: Ok to use native Python3's code type
                code = Code(co_argcount, kwonlyargcount, co_nlocals, co_stacksize, co_flags,
                            co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                            co_firstlineno, bytes(co_lnotab, encoding='utf-8'),
                            co_freevars, co_cellvars)
        else:
            code =  Code(co_argcount, kwonlyargcount, co_nlocals, co_stacksize, co_flags,
                        co_code, co_consts, co_names, co_varnames, co_filename, co_name,
                        co_firstlineno, bytes(co_lnotab, encoding='utf-8'),
                        co_freevars, co_cellvars)
    else:
        if (3000 <= magic_int < 20121):
            # Python 3 encodes some fields as Unicode while Python2
            # requires the corresponding field to have string values
            co_consts = tuple([compat_u2s(s) if isinstance(s, unicode)
                                   else s for s in co_consts])
            co_names  = tuple([compat_u2s(s) if isinstance(s, unicode)
                                   else s for s in co_names])
            co_varnames  = tuple([compat_u2s(s) if isinstance(s, unicode)
                                      else s for s in co_varnames])
            co_filename = str(co_filename)
            co_name = str(co_name)
        if 3020 < magic_int <= 20121:
            code =  Code3(co_argcount, kwonlyargcount,
                          co_nlocals, co_stacksize, co_flags, co_code,
                          co_consts, co_names, co_varnames, co_filename, co_name,
                          co_firstlineno, co_lnotab, co_freevars, co_cellvars)
        else:
            Code = types.CodeType
            code =  Code(co_argcount, co_nlocals, co_stacksize, co_flags, co_code,
                         co_consts, co_names, co_varnames, co_filename, co_name,
                         co_firstlineno, co_lnotab, co_freevars, co_cellvars)
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

# FIXME: redo with a dispatch table same as
# marshal.
# In marshal.c this method is called r_object()
def load_code_internal(fp, magic_int, bytes_for_s=False,
                       code_objects={}):
    global internStrings, internObjects

    b1 = ord(fp.read(1))

    flag = False
    if b1 & FLAG_REF:
        # Since 3.4, "flag" is the marshal.c name
        flag = True
        b1 = b1 & (FLAG_REF-1)
    marshalType = chr(b1)

    # print(marshalType) # debug
    if marshalType == '0':
        # In C this NULL. Not sure what it should
        # translate here. Note NULL != None which is below
        return None
    elif marshalType == 'N':
        return None
    elif marshalType == 'S':
        return StopIteration
    elif marshalType == '.':
        return Ellipsis
    elif marshalType == 'F':
        return False
    elif marshalType == 'T':
        return True
    elif marshalType == 'i':
        # int32
        return r_ref(int(unpack('<i', fp.read(4))[0]), flag)
    elif marshalType == 'l':
        # long
        n = unpack('<i', fp.read(4))[0]
        if n == 0:
            return long(0)
        size = abs(n)
        d = long(0)
        for j in range(0, size):
            md = int(unpack('<h', fp.read(2))[0])
            d += md << j*15
        if n < 0:
            d = long(d*-1)
        return r_ref(d, flag)
    elif marshalType == 'I':
        # int64. Python 3.4 removed this.
        return unpack('<q', fp.read(8))[0]
    elif marshalType == 'f':
        # float - Seems not in use after Python 2.4
        strsize = unpack('B', fp.read(1))[0]
        s = fp.read(strsize)
        return r_ref(float(s), flag)
    elif marshalType == 'g':
        # binary float
        return r_ref(float(unpack('<d', fp.read(8))[0]), flag)
    elif marshalType == 'x':
        # complex
        if magic_int <= 62061:
            get_float = lambda: float(fp.read(unpack('B', fp.read(1))[0]))
        else:
            get_float = lambda: float(fp.read(unpack('<i', fp.read(4))[0]))
        real = get_float()
        imag = get_float()
        return r_ref(complex(real, imag), flag)
    elif marshalType == 'y':
        # binary complex
        real = unpack('<d', fp.read(8))[0]
        imag = unpack('<d', fp.read(8))[0]
        return r_ref(complex(real, imag), flag)
    elif marshalType == 's':
        # string
        # Note: could mean bytes in Python3 processing Python2 bytecode
        strsize = unpack('<i', fp.read(4))[0]
        s = fp.read(strsize)
        if not bytes_for_s:
            s = compat_str(s)
        return r_ref(s, flag)
    elif marshalType == 'A':
        # ascii interned - Python3 3.4
        # FIXME: check
        strsize = unpack('<i', fp.read(4))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return r_ref(interned, flag)
    elif marshalType == 'a':
        # ascii. Since Python 3.4
        strsize = unpack('<i', fp.read(4))[0]
        s = fp.read(strsize)
        s = compat_str(s)
        return r_ref(s, flag)
    elif marshalType == 'z':
        # short ascii - since Python 3.4
        strsize = unpack('B', fp.read(1))[0]
        return r_ref(compat_str(fp.read(strsize)), flag)
    elif marshalType == 'Z':
        # short ascii interned - since Python 3.4
        # FIXME: check
        strsize = unpack('B', fp.read(1))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return r_ref(interned, flag)
    elif marshalType == 't':
        # interned - since Python 3.4
        strsize = unpack('<i', fp.read(4))[0]
        interned = compat_str(fp.read(strsize))
        internStrings.append(interned)
        return r_ref(interned, flag)
    elif marshalType == 'u':
        strsize = unpack('<i', fp.read(4))[0]
        unicodestring = fp.read(strsize)
        if PYTHON_VERSION == 3.2 and IS_PYPY:
            # FIXME: this isn't quite right. See
            # pypy3-2.4.0/lib-python/3/email/message.py
            # '([^\ud800-\udbff]|\A)[\udc00-\udfff]([^\udc00-\udfff]|\Z)')
            return r_ref(unicodestring.decode('utf-8', errors='ignore'), flag)
        else:
            return r_ref(unicodestring.decode('utf-8'), flag)
    elif marshalType == ')':
        # small tuple - since Python 3.4
        tuplesize = unpack('B', fp.read(1))[0]
        ret, i = r_ref_reserve(tuple(), flag)
        while tuplesize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            tuplesize -= 1
            pass
        return r_ref_insert(ret, i)
    elif marshalType == '(':
        # tuple
        tuplesize = unpack('<i', fp.read(4))[0]
        ret = r_ref(tuple(), flag)
        while tuplesize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            tuplesize -= 1
        return ret
    elif marshalType == '[':
        # list. FIXME: check me
        n = unpack('<i', fp.read(4))[0]
        ret = r_ref(list(), flag)
        while n > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            tuplesize -= 1
        return ret
    elif marshalType == '{':
        ret = r_ref(dict(), flag)
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
    elif marshalType in ['<', '>']:
        # set and frozenset
        setsize = unpack('<i', fp.read(4))[0]
        ret, i = r_ref_reserve(tuple(), flag)
        while setsize > 0:
            ret += load_code_internal(fp, magic_int, code_objects=code_objects),
            setsize -= 1
        if marshalType == '>':
            return r_ref_insert(frozenset(ret), i)
        else:
            return r_ref_insert(set(ret), i)
    elif marshalType == 'R':
        # Python 2 string reference
        refnum = unpack('<i', fp.read(4))[0]
        return internStrings[refnum]
    elif marshalType == 'c':
        return load_code_type(fp, magic_int, bytes_for_s=False,
                              code_objects=code_objects)
    elif marshalType == 'C':
        # code type used in Python 1.0 - 1.2
        raise KeyError("C code is Python 1.0 - 1.2; can't handle yet")
    elif marshalType == 'r':
        # object reference - since Python 3.4
        refnum = unpack('<i', fp.read(4))[0]
        o = internObjects[refnum-1]
        return o
    elif marshalType == '?':
        # unknown
        raise KeyError(marshalType)
    else:
        sys.stderr.write("Unknown type %i (hex %x) %c\n" %
                         (ord(marshalType), ord(marshalType), ord(marshalType)))
    return
