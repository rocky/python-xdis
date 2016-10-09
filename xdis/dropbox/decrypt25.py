#!/usr/bin/env python
# Copyright Hagen Fritsch, 2012, License: GPL-2.0
# Adaption and generalization for xdis use by Rocky Bernstein

# Dropbox Python bytecode decryption tool for Dropbox versions of 1.1x
# (and possibly earlier) which uses Python bytecode 2.5.

from __future__ import print_function

import types
import struct

from xdis import PYTHON3
import xdis.marsh as xmarshal

def rng(a, b):
    b = ((b << 13) ^ b) & 0xffffffff
    c = (b ^ (b >> 17))
    c = (c ^ (c << 5))
    return (a * 69069 + c + 0x6611CB3B) & 0xffffffff

# this is replaced by mersenne in newer versions
def get_keys(a, b):
    ka = rng(a,b)
    kb = rng(ka, a)
    kc = rng(kb, ka)
    kd = rng(kc, kb)
    ke = rng(kd, kc)
    return (kb,kc,kd,ke)

def MX(z, y, sum, key, p, e):
    return (((z>>5^y<<2) + (y>>3^z<<4)) ^ ((sum^y) + (key[(p&3)^e] ^ z)))

def tea_decipher(v, key):
    """
    Tiny Decryption Algorithm decription (TEA)
    See https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm
    """
    DELTA = 0x9e3779b9
    n = len(v)
    rounds = 6 + 52//n
    sum = (rounds*DELTA)
    y = v[0]
    while sum != 0:
        e = (sum >> 2) & 3
        for p in range(n-1, -1, -1):
            z = v[(n+p-1)%n]
            v[p] = (v[p] - MX(z,y,sum,key,p,e)) & 0xffffffff
            y = v[p]
        sum -= DELTA
    return v

def load_code(self):
    """
    Returns a Python code object like xdis.unmarshal.load_code(),
    but in we decrypt the data in self.bufstr.

    That is:
      * calculate the TEA key,
      * decrypt self.bufstr
      * create and return a Python code-object
    """
    a = self.load_int()
    b = self.load_int()
    key = get_keys(a, b)
    padsize = (b + 15) & ~0xf
    intsize = padsize/4
    data = self.bufstr[self.bufpos:self.bufpos+padsize]
    # print("%d: %d (%d=%d)" % (self.bufpos, b, padsize, len(data)))
    data = list(struct.unpack('<%dL' % intsize, data))
    tea_decipher(data, key)
    self.bufpos += padsize
    obj = xmarshal._FastUnmarshaller(struct.pack('<%dL' % intsize, *data))
    code = obj.load_code()
    co_code = patch(code.co_code)
    if PYTHON3:
        return types.CodeType(code.co_argcount, 0, code.co_nlocals, code.co_stacksize,
                              code.co_flags,
                              co_code, code.co_consts, code.co_names, code.co_varnames,
                              code.co_filename, code.co_name, code.co_firstlineno,
                              code.co_lnotab, code.co_freevars, code.co_cellvars)
    else:
        return types.CodeType(code.co_argcount, code.co_nlocals, code.co_stacksize, code.co_flags,
                              co_code, code.co_consts, code.co_names, code.co_varnames,
                              code.co_filename, code.co_name, code.co_firstlineno,
                              code.co_lnotab, code.co_freevars, code.co_cellvars)

try:
    a = bytearray()
except:
    class bytearray(object):
        def __init__(self, s):
            self.l = map(ord, s)
        def __setitem__(self, idx, val):
            self.l[idx] = val
        def __getitem__(self, idx):
            return self.l[idx]
        def __str__(self):
            return ''.join(map(chr, self.l))
        def __len__(self):
            return len(self.l)

# Automatically generated opcode substitution table for v1
# A different dropbox table for v.2 table is at
#   https://github.com/kholia/dedrop/blob/master/src/dedrop-v2/dedrop-v2.py
# They are similar but not the same.
table = {  0:   0,   1:  87,  2:  66,  4:  25,  6:  55,  7:  62,
           9:  71,  10:  79, 12:  21, 13:   4, 14:  72, 15:   1, 16: 30,
          17:  31,  18:  32, 19:  33, 22:  63,
          26:  86,  29:  56, 31:  60,
          33:  73,  34:  15, 35:  74, 36:  20, 38:  12, 39: 68, 40:  80,
          41:  22,  42:  89, 43:  26, 50:  64, 51:  82, 52:  23, 54: 11,
          55:  24,
          56:  84,  59:   2, 60:   3, 61:  40, 62:  41, 63:  42, 64: 43,
          65:  85,  66:  83, 67:  88, 68:  18, 69:  61, 70: 116, 71: 126,
          72: 100,
          73: 110,  74: 120, 75: 122, 76: 132,
          77: 133,  78: 104, 79: 101, 80: 102,
          81:  93,  82: 125, 83: 111, 84:  95, 85: 134, 86: 105,
          88: 107,  89: 108, 90: 112, 91: 130, 92: 124,
          93:  92,  94:  91, 95:  90,
          97: 135,  99: 136, 100: 137, 101: 106,
         102: 131, 103: 113, 104:  99,
         105:  97, 106: 121, 107: 103, 111: 140,
         112: 141,
         113: 142}

# manual mapping of the rest
table[37] = 81
table[28] = 19
table[87] = 96
table[21] = 65
table[96] = 119
table[8] = 57
table[32] = 28
table[44] = 50
table[45] = 51
table[46] = 52
table[47] = 53
table[23] = 78
table[24] = 77
table[3] = 59
table[11] = 75
table[58] = 76

misses = {}

def patch(code):
    code = bytearray(code)
    i = 0
    n = len(code)
    while i < n:
        op = code[i]
        if not op in table:
            print("missing opcode %d. code: " % op, repr(str(code)))
            misses[op] = misses.get(op, 0) + 1
        code[i] = table.get(op,op)
        i += 1
        if table.get(op,op) >= 90: #opcode.HAVE_ARGUMENT:
            i += 2
    return bytes(code) if PYTHON3 else str(code)

try: from __pypy__ import builtinify
except ImportError: builtinify = lambda f: f

@builtinify
def loads(s):
    """
    xdis.marshal.load() but with its dispatch load_code() function replaced
    with our decoding version.
    """
    um = xmarshal._FastUnmarshaller(s)
    um.dispatch[xmarshal.TYPE_CODE] = load_code
    return um.load()

def fix_dropbox_pyc(fp, fixed_pyc='/tmp/test.pyc'):
    source_size = struct.unpack("I", fp.read(4))[0] # size mod 2**32
    ts = fp.read(4)
    timestamp = struct.unpack("I", ts)[0]
    b = fp.read()
    co = loads(b)
    return 2.5, timestamp, 62131, co, False, source_size

def fix_dir(path):
    import os
    for root, dirs, files in os.walk(path):
        for name in files:
            if not name.endswith('pyc'): continue
            name = os.path.join(root, name)
            print("fixing", name)
            data = open(name).read()
            try:
                c = xmarshal.loads(data[8:])
            except Exception as e:
                print("error", e, repr(e))
                # print repr(data[8:])
                continue
            # fix the version indicator and save
            open(name, "w").write(
                "\xb3\xf2\r\n" + data[4:8] + xmarshal.dumps(c))

if __name__ == '__main__':
    import os, sys
    if sys.argv != 2:
        print("Usage: %s python-file" % os.path.basename(sys.argv[0]))
        sys.exit(1)

    fix_dir(sys.argv[1])

# for the sake of completeness, here are the code-fragments to automatically generate
# the opcode substitution table
if 0:
    import marshal
    def fill(c, d):
        if len(c.co_code) != len(d.co_code):
            print("len mismatch", c, d)
            return
        for i, j in zip(c.co_code, d.co_code):
            # if i in m and not table[i] == j:
            #    print "mismatch %c (%x) => %c (%x)" % (ord(i),ord(i),ord(j),ord(j))
            v = table.setdefault(i, {})
            v[j] = v.get(j, 0) + 1
            pass
        return


    for root, dirs, files in os.walk('library'):
        for name in files:
            name = os.path.join(root, name)
            if not name.endswith('pyc'): continue
            f2 = os.path.join('/tmp/python-defaults-2.7.2/Python-2.5.4/Lib', name[8:])
            if not os.path.exists(f2): continue
            print("loading", name)
            try:
                c = xmarshal.loads(open(name).read()[8:])
            except:
                print("error", name)
                continue
            d =  marshal.loads(open(f2).read()[8:])
            fill(c, d)
            codes_c = filter(lambda x: type(x) == type(c), c.co_consts)
            codes_d = filter(lambda x: type(x) == type(c), d.co_consts)
            for i,j in zip(codes_c, codes_d):
                fill(i,j)
                pass
            pass


    def print_table(m):
        k = m.keys()
        k.sort()
        table = {}
        for i in k:
            print("%c (%02x %s) =>" %
                  (ord(i), ord(i), bin(ord(i))), end='')
            for j,count in m[i].iteritems():
                if j == i: continue
                table[ord(i)] = ord(j)
                print("\t%c (%02x %s) [%d]" %
                      (ord(j), ord(j), bin(ord(j)), count), end="")
                # print("%c (%02x %s) => %c (%02x %s)\t%d\t%s" % (ord(i),ord(i),bin(ord(i)),ord(j),ord(j),bin(ord(j)),ord(j)-ord(i),bin(ord(i)^ord(j)|0x100).replace('0', ' ')))
            print()
        return table


    import re
    re.compile('offset loc_(\w+)').findall('dd offset loc_8096DC4, offset loc_8096963, offset loc_8095462')

    def load(name):
        a = re.compile('offset loc_(\w+)').findall(open(name).read())
        a = [int(i,16) for i in a]
        c = a[:]
        c.sort()
        c = [(i, c.index(i)) for i in a]
        d = {}
        for i, (addr, pos) in enumerate(c):
            d[addr] = (i, pos)
        return c, d
