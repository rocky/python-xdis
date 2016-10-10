"""
CPython 1.5 bytecode opcodes

This is used in bytecode disassembly. This is similar to the
opcodes in Python's dis.py library.
"""

from xdis.bytecode import _findlabels as findlabels
from xdis.bytecode import _findlinestarts as findlinestarts

# FIXME: can we DRY this even more?

hasArgumentExtended = []

cmp_op = ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is',
        'is not', 'exception match', 'BAD')

hasconst = []
hasname = []
hasjrel = []
hasjabs = []
haslocal = []
hascompare = []
hasfree = []
hasnargs = []  # For function-like calls
hasvargs = []  # Similar but for operators BUILD_xxx

opmap = {}
opname = [''] * 256
for op in range(256): opname[op] = '<%r>' % (op,)
del op

def def_op(name, op):
    opname[op] = name
    opmap[name] = op

def compare_op(name, op):
    def_op(name, op)
    hascompare.append(op)

def const_op(name, op):
    def_op(name, op)
    hasconst.append(op)

def free_op(name, op):
    def_op(name, op)
    hasfree.append(op)

def jabs_op(name, op):
    def_op(name, op)
    hasjabs.append(op)

def jrel_op(name, op):
    def_op(name, op)
    hasjrel.append(op)

def local_op(name, op):
    def_op(name, op)
    haslocal.append(op)

def name_op(name, op):
    def_op(name, op)
    hasname.append(op)

def nargs_op(name, op):
    def_op(name, op)
    hasnargs.append(op)

def varargs_op(name, op):
    def_op(name, op)
    hasvargs.append(op)


# Instruction opcodes for compiled code
# Blank lines correspond to available opcodes

def_op('STOP_CODE', 0)
def_op('POP_TOP', 1)
def_op('ROT_TWO', 2)
def_op('ROT_THREE', 3)
def_op('DUP_TOP', 4)

def_op('UNARY_POSITIVE', 10)
def_op('UNARY_NEGATIVE', 11)
def_op('UNARY_NOT', 12)
def_op('UNARY_CONVERT', 13)

def_op('UNARY_INVERT', 15)

def_op('BINARY_POWER', 19)

def_op('BINARY_MULTIPLY', 20)
def_op('BINARY_DIVIDE', 21)
def_op('BINARY_MODULO', 22)
def_op('BINARY_ADD', 23)
def_op('BINARY_SUBTRACT', 24)
def_op('BINARY_SUBSCR', 25)

def_op('SLICE+0', 30)
def_op('SLICE+1', 31)
def_op('SLICE+2', 32)
def_op('SLICE+3', 33)

def_op('STORE_SLICE+0', 40)
def_op('STORE_SLICE+1', 41)
def_op('STORE_SLICE+2', 42)
def_op('STORE_SLICE+3', 43)

def_op('DELETE_SLICE+0', 50)
def_op('DELETE_SLICE+1', 51)
def_op('DELETE_SLICE+2', 52)
def_op('DELETE_SLICE+3', 53)

def_op('STORE_SUBSCR', 60)
def_op('DELETE_SUBSCR', 61)

def_op('BINARY_LSHIFT', 62)
def_op('BINARY_RSHIFT', 63)
def_op('BINARY_AND', 64)
def_op('BINARY_XOR', 65)
def_op('BINARY_OR', 66)

def_op('PRINT_EXPR', 70)
def_op('PRINT_ITEM', 71)
def_op('PRINT_NEWLINE', 72)

def_op('BREAK_LOOP', 80)

def_op('LOAD_LOCALS', 82)
def_op('RETURN_VALUE', 83)

def_op('EXEC_STMT', 85)

def_op('POP_BLOCK', 87)
def_op('END_FINALLY', 88)
def_op('BUILD_CLASS', 89)

HAVE_ARGUMENT = 90              # Opcodes from here have an argument:

name_op('STORE_NAME', 90)       # Index in name list
name_op('DELETE_NAME', 91)      # ""
varargs_op('UNPACK_TUPLE', 92)  # Number of tuple items
def_op('UNPACK_LIST', 93)	# Number of list items
name_op('STORE_ATTR', 95)       # Index in name list
name_op('DELETE_ATTR', 96)      # ""
name_op('STORE_GLOBAL', 97)     # ""
name_op('DELETE_GLOBAL', 98)    # ""

const_op('LOAD_CONST', 100)     # Index in const list
name_op('LOAD_NAME', 101)       # Index in name list
varargs_op('BUILD_TUPLE', 102)  # Number of tuple items
varargs_op('BUILD_LIST', 103)   # Number of list items
varargs_op('BUILD_MAP', 104)    # Always zero for now
name_op('LOAD_ATTR', 105)       # Index in name list
compare_op('COMPARE_OP', 106)       # Comparison operator

name_op('IMPORT_NAME', 107)     # Index in name list
name_op('IMPORT_FROM', 108)     # Index in name list

jrel_op('JUMP_FORWARD', 110)    # Number of bytes to skip
jrel_op('JUMP_IF_FALSE', 111)   # ""
jrel_op('JUMP_IF_TRUE', 112)    # ""
jabs_op('JUMP_ABSOLUTE', 113)   # Target byte offset from beginning of code
jrel_op('FOR_LOOP', 114)	# Number of bytes to skip

name_op('LOAD_GLOBAL', 116)     # Index in name list

jrel_op('SETUP_LOOP', 120)      # Distance to target address
jrel_op('SETUP_EXCEPT', 121)    # ""
jrel_op('SETUP_FINALLY', 122)   # ""

local_op('LOAD_FAST', 124)      # Local variable number
local_op('STORE_FAST', 125)     # Local variable number
local_op('DELETE_FAST', 126)    # Local variable number
def_op('SET_LINENO', 127)	# Current line number

def_op('RAISE_VARARGS',  130)   # Number of raise arguments (1, 2, or 3)
nargs_op('CALL_FUNCTION', 131)   # #args + (#kwargs << 8)

def_op('MAKE_FUNCTION', 132)    # Number of args with default values
varargs_op('BUILD_SLICE', 133)   # Number of items

EXTENDED_ARG = 143

fields2copy = """cmp_op hasjabs""".split()

def def_op(opname, opmap, name, op):
    opname[op] = name
    opmap[name] = op

def rm_op(name, op, l):
    # opname is an array, so we need to keep the position in there.
    l['opname'][op] = ''

    if op in l['hasconst']:
       l['hasconst'].remove(op)
    if op in l['hascompare']:
       l['hascompare'].remove(op)
    if op in l['hasfree']:
       l['hasfree'].remove(op)
    if op in l['hasjabs']:
       l['hasjabs'].remove(op)
    if op in l['hasname']:
       l['hasname'].remove(op)
    if op in l['hasjrel']:
       l['hasjrel'].remove(op)
    if op in l['haslocal']:
       l['haslocal'].remove(op)
    if op in l['hasname']:
       l['hasname'].remove(op)
    if op in l['hasnargs']:
       l['hasnargs'].remove(op)
    if op in l['hasvargs']:
       l['hasvargs'].remove(op)

    assert l['opmap'][name] == op
    del l['opmap'][name]

def updateGlobal():
    globals().update({'python_version': 1.5})
    # Canonicalize to PJIx: JUMP_IF_y and POP_JUMP_IF_y
    globals().update({'PJIF': opmap['JUMP_IF_FALSE']})
    globals().update({'PJIT': opmap['JUMP_IF_TRUE']})

    globals().update({'JUMP_OPs': map(lambda op: opname[op],
                                      hasjrel + hasjabs)})
    globals().update(dict([(k.replace('+', '_'), v) for (k, v) in opmap.items()]))
    return

updateGlobal()

def dump_opcodes(opmap):
    """Utility for dumping opcodes"""
    op2name = {}
    for k in opmap.keys():
        op2name[opmap[k]] = k
    for i in sorted(op2name.keys()):
        print("%-3s %s" % (str(i), op2name[i]))
